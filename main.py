import os
import warnings
import json
import logging
from graphql_client import GraphQLClient
from data_processor import DataProcessor
from logger_setup import LoggerSetup
from time_manager import TimeManager

def main():
    log_file = LoggerSetup.setup_logging()
    logging.info("Приложение для обновления статусов ПОС запущено.", extra={'highlight': True})

    # Отключение предупреждений о небезопасных запросах HTTPS
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    # Загрузка конфигурации
    config_path = os.path.join('config', 'processing_config.json')
    state_path = os.path.join('state', 'state.json')
    server_config_path = os.path.join('config', 'servern_config.json')

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    with open(server_config_path, 'r', encoding='utf-8') as f:
        server_config = json.load(f)
        
    utc_offset_hours = config['utcOffsetHours']
    time_manager = TimeManager(state_path, utc_offset_hours)
    
    first = config['pagination']['pageSize']
    status_map = config['statusMapping']

    # Получение start_time и end_time
    start_time = time_manager.get_start_time()
    end_time = time_manager.get_end_time()

    # Проверка диапазона дат
    if not time_manager.is_date_range_valid(start_time, end_time):
        raise ValueError("Диапазон дат не должен превышать 14 дней.")

    logging.info(f"Загружена конфигурация: размер страницы - {first}, "
                 f"начальная дата - {start_time}, конечная дата - {end_time}.")

    raw_data = []
    
    variables = {
        "first": first,
        "after": None,
        "docRcinsDateGreater": start_time,
        "docRcinsDateLess": end_time
    }
    
    query_path = os.path.join('queries', 'query_ArRubricValue.graphql')

    try:
        with GraphQLClient(server_config) as graphql_client:
            logging.info("Подключение к серверу ДЕЛО установлено.", extra={'highlight': True})
            
            while True:
                # Выполнение запроса для получения данных
                response = graphql_client.execute_query(query_path, variables)
                print(json.dumps(response, indent=4, ensure_ascii=False))
                edges = response['data']['arRubricValuesPg']['edges']
                pageInfo = response['data']['arRubricValuesPg']['pageInfo']

                # Сохранение полученных данных
                raw_data.extend([edge['node'] for edge in edges])
                logging.info(f"Получено {len(edges)} записей.")

                # Проверка наличия следующей страницы и достижения максимального количества элементов
                if not pageInfo['hasNextPage']:
                    logging.info("Получены все РК в диапазоне дат")
                    break

                # Обновление переменных для следующего запроса
                variables['after'] = pageInfo['endCursor']

            # Обработка данных и формирование пакетов мутаций
            mutation_queries, docrc_list = DataProcessor.process_and_build_mutation_queries(raw_data, status_map)
            if not mutation_queries:
                logging.info("Нет РК для обновления.", extra={'highlight': True})
                return
            
            logging.info(f"Количество РК для обновления: {len(docrc_list)}", extra={'highlight': True})
            logging.info(f"Список РК для обновления: {docrc_list}")
            logging.info(f"Сформировано {len(mutation_queries)} пакетов мутаций для выполнения.")

            # Выполнение пакетных мутаций
            # for mutation_query in mutation_queries:
            #     mutation_response = graphql_client.execute_query(mutation_query)
            #     logging.info(f"Ответ на мутацию: {mutation_response}")
        # Сохранение времени последнего успешного запуска
        time_manager.write_state(end_time)

    except Exception as e:
        logging.error(f"Ошибка при при вополнии запроса к серверу: {e}")

    logging.info(f"Выполнение приложения завершено. Подробная информация в файле {log_file}", extra={'highlight': True})

if __name__ == '__main__':
    main()
