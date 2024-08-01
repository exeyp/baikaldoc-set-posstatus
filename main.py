import os
import warnings
import json
from graphql_client import GraphQLClient
from data_processor import DataProcessor


def main():
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

    raw_data = []
    
    variables = {
        "first": first,
        "after": None,
        "docRcinsDateGreater": start_date,
        "docRcinsDateLess": end_date
        }
    
    query_path = os.path.join('queries', 'query_ArRubricValue.graphql')
    # mutation_path = os.path.join('queries', 'mutation_UpdateArRubricValue.graphql')

    with GraphQLClient() as graphql_client:
        while True:
            # Выполнение запроса для получения данных
            response = graphql_client.execute_query(query_path, variables)
            # print(json.dumps(response, indent=4, ensure_ascii=False))
            edges = response['data']['arRubricValuesPg']['edges']
            pageInfo = response['data']['arRubricValuesPg']['pageInfo']

            # Сохранение полученных данных
            raw_data.extend([edge['node'] for edge in edges])

            # Проверка наличия следующей страницы и достижения максимального количества элементов
            if not pageInfo['hasNextPage']:
                break

            # Обновление переменных для следующего запроса
            variables['after'] = pageInfo['endCursor']

        # Обработка данных и формирование пакетов мутаций
        mutation_queries  = DataProcessor.process_and_build_mutation_queries(raw_data, status_map)
        
        # Выполнение пакетных мутаций
        for mutation_query in mutation_queries:
            mutation_response = graphql_client.execute_query(mutation_query)
            print(json.dumps(mutation_response, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    main()