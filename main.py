import os
import json
from graphql_client import GraphQLClient


def main():
    config_path = os.path.join('config', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    start_date = config['start_date']
    end_date = config['end_date']

    query_path = os.path.join('queries', 'query.graphql')
    variables = {
    # "start_date": start_date,
    # "end_date": end_date
    }

    with GraphQLClient(config_path) as graphql_client:
        response = graphql_client.execute_query(query_path, variables)
        # print(json.dumps(response, indent=4, ensure_ascii=False))
if __name__ == '__main__':
    main()