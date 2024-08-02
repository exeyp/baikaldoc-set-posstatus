import os
import warnings
import json
import logging
from graphql_client import GraphQLClient
from data_processor import DataProcessor
from logger_setup import LoggerSetup

def main():
    LoggerSetup.setup_logging()
    logging.info("Приложение для обновления статусов ПОС запущено.")

    # Отключение предупреждений о небезопасных запросах HTTPS
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    # Загрузка конфигурации
    config_path = os.path.join('config', 'processing_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    first = config['pagination']['pageSize']
    start_date = config['dateFilter']['startDate']
    end_date = config['dateFilter']['endDate']
    status_map = config['statusMapping']

    logging.info(f"Загружена конфигурация: размер страницы - {first}, "
                 f"начальная дата - {start_date}, конечная дата - {end_date}.")

    raw_data = []
    
    variables = {
        "first": first,
        "after": None,
        "docRcinsDateGreater": start_date,
        "docRcinsDateLess": end_date
    }
    
    query_path = os.path.join('queries', 'query_ArRubricValue.graphql')

    with GraphQLClient() as graphql_client:
        logging.info("Подключение к GraphQL API установлено.")
        
        while True:
            # Выполнение запроса для получения данных
            response = graphql_client.execute_query(query_path, variables)
            edges = response['data']['arRubricValuesPg']['edges']
            pageInfo = response['data']['arRubricValuesPg']['pageInfo']

            # Сохранение полученных данных
            raw_data.extend([edge['node'] for edge in edges])
            logging.info(f"Получено {len(edges)} записей.")

            # Проверка наличия следующей страницы и достижения максимального количества элементов
            if not pageInfo['hasNextPage']:
                logging.info("Получены все доступные данные.")
                break

            # Обновление переменных для следующего запроса
            variables['after'] = pageInfo['endCursor']

        # Обработка данных и формирование пакетов мутаций
        mutation_queries = DataProcessor.process_and_build_mutation_queries(raw_data, status_map)
        if not mutation_queries:
            logging.info("Нет мутаций для выполнения.")
            return

        logging.info(f"Сформировано {len(mutation_queries)} пакетов мутаций для выполнения.")

        # Выполнение пакетных мутаций
        for mutation_query in mutation_queries:
            mutation_response = graphql_client.execute_query(mutation_query)
            logging.info(f"Ответ на мутацию: {mutation_response}")

    logging.info("Приложение завершено.")

if __name__ == '__main__':
    main()
