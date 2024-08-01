import os
import requests
import json

class GraphQLClient:
    def __init__(self):
        config_path = os.path.join('config', 'server_config.json')
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = json.load(file)
        self.session = requests.Session()
    
    def login(self):
        login_payload = {
            'user': self.config['username'],
            'password': self.config['password'],
            'items': {'app': self.config['app']}
        }
        response = self.session.post(self.config['login_url'], json=login_payload, verify=False)
        if response.status_code != 200:
            response.raise_for_status()
    
    def logout(self):
        response = self.session.post(self.config['logout_url'], verify=False)
        if response.status_code != 200:
            response.raise_for_status()

    def execute_query(self, query, variables=None):
        if query.endswith('.graphql'):
            with open(query, 'r', encoding='utf-8') as file:
                query = file.read()
        response = self.session.post(self.config['graphql_endpoint'], json={'query': query, 'variables': variables}, verify=False)
        if response.status_code != 200:
            response.raise_for_status()
        result = response.json()
        if 'errors' in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        return result

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
