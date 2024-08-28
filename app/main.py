import os
import warnings
import json
import logging
import time
from app.graphql_client import GraphQLClient
from app.data_processor import DataProcessor
from app.logger_setup import LoggerSetup
from app.time_manager import TimeManager

def main():
    # Настройка логирования
    log_file = LoggerSetup.setup_logging()
    logging.info("Приложение для обновления статусов ПОС запущено.", extra={'highlight': True})

    # Отключение предупреждений о небезопасных запросах HTTPS
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    # Загрузка конфигурации обработки
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'processing_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Загрузка конфигурации подключения
    connection_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'connection_config.json')
    with open(connection_config_path, 'r', encoding='utf-8') as f:
        connection_config = json.load(f)
        
    # Извлечение параметров из конфигурации
    status_map = config['statusMapping']
    page_size = config['pagination'].get('pageSize', 100)
    utc_offset_hours = config.get('utcOffsetHours', 0)
    max_date_range_days = config['dateRange'].get('maxDateRangeDays', 14)
    fixed_start_time = config['dateRange'].get('startDate')
    fixed_end_time = config['dateRange'].get('endDate')
    use_fixed_dates = config['dateRange'].get('useFixedDates', False)
    retry_attempts = config.get('retryAttempts', 3)

    # Управление временем и проверка диапазона дат
    if not os.path.exists('state'):
        os.makedirs('state')
    state_path = os.path.join(os.path.dirname(__file__), '..', 'state', 'state.json')
    time_manager = TimeManager(state_path, utc_offset_hours)
    
    if use_fixed_dates:
        start_time = time_manager.get_start_time(max_date_range_days, fixed_start_time)
        end_time = time_manager.get_end_time(fixed_end_time)
    else:
        start_time = time_manager.get_start_time(max_date_range_days)
        end_time = time_manager.get_end_time()
        # Проверка и корректировка диапазона, если параметры не заданы вручную
        start_time, end_time = time_manager.adjust_date_range(start_time, end_time, max_date_range_days)

    logging.info(f"Загружена конфигурация: размер страницы - {page_size}, "
                 f"начальная дата - {start_time}, конечная дата - {end_time}.")

    raw_data = []
    variables = {
        "first": page_size,
        "after": None,
        # "docRcinsDateGreater": start_time,
        # "docRcinsDateLess": end_time,
        "refRubricisnDateGreater": start_time,
        "refRubricisnDateLess": end_time
    }
    
    query_path = os.path.join(os.path.dirname(__file__), '..', 'queries', 'query_ArRubricValue.graphql')

    try:
        # Подключение к GraphQL API
        with GraphQLClient(connection_config) as graphql_client:
            logging.info("Подключение к серверу ДЕЛО установлено.", extra={'highlight': True})
            
            while True:
                # Выполнение запроса для получения данных
                response = graphql_client.execute_query(query_path, variables)
                # print(json.dumps(response, indent=4, ensure_ascii=False))
                edges = response['data']['arRubricValuesPg']['edges']
                pageInfo = response['data']['arRubricValuesPg']['pageInfo']

                # Сохранение полученных данных
                raw_data.extend([edge['node'] for edge in edges])
                logging.info(f"Получено {len(edges)} записей.")

                # Проверка наличия следующей страницы и достижения максимального количества элементов
                if not pageInfo['hasNextPage']:
                    logging.info("Получены все РК в диапазоне дат.")
                    break

                # Обновление переменных для следующего запроса
                variables['after'] = pageInfo['endCursor']

            # Обработка данных и формирование пакетов мутаций
            mutation_queries, docrc_list = DataProcessor.process_and_build_mutation_queries(raw_data, status_map)
            if not mutation_queries:
                logging.info("Нет РК для обновления.", extra={'highlight': True})
                return
            
            logging.info(f"Количество РК для обновления: {len(docrc_list)}", extra={'highlight': True})
            logging.info(f"Список ID РК для обновления: {docrc_list}")
            logging.info(f"Сформировано {len(mutation_queries)} пакетов мутаций для выполнения.")

            # Выполнение пакетных мутаций
            for mutation_query in mutation_queries:
                for attempt in range(retry_attempts):
                    try:
                        mutation_response = graphql_client.execute_query(mutation_query)
                        logging.info(f"Ответ на мутацию: {mutation_response}")
                        break
                    except Exception as e:
                        logging.error(f"Ошибка выполнения запроса (попытка {attempt+1} из {retry_attempts}): {e}")
                        time.sleep(5)
                else:
                    logging.error("Не удалось выполнить мутацию после нескольких попыток.")
                    return

        # Сохранение времени последнего успешного запуска
        time_manager.write_state(end_time)

    except Exception as e:
        logging.error(f"Ошибка при выполнении запроса к серверу: {e}")

    logging.info(f"Выполнение приложения завершено. Подробная информация в файле {log_file}", extra={'highlight': True})

if __name__ == '__main__':
    main()
