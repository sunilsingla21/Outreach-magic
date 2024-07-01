import os

import requests
from dotenv import load_dotenv
from google.api_core.exceptions import AlreadyExists
from google.cloud import secretmanager


class SecretManager:
    def __new__(cls):
        '''
        Singleton pattern to have a single instance everywhere
        '''
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, 'project_id'):
            load_dotenv('.env')
            self.project_id = self.get_project_id()

    def get_project_id(self):
        metadata_url = 'http://metadata.google.internal/computeMetadata/v1/project/project-id'
        headers = {'Metadata-Flavor': 'Google'}

        try:
            response = requests.get(metadata_url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses

            return response.text
        except requests.exceptions.ConnectionError as e:
            print('Detected running locally. Getting variables from .env file')
            load_dotenv('local-environment.env', override=True)
            return None
        except requests.exceptions.RequestException as e:
            print(f'Error retrieving project ID: {e}')
            raise e

    def __get_from_google(self, secret_id, version_id):
        client = secretmanager.SecretManagerServiceClient()
        secret_name = f'projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}'
        response = client.access_secret_version(name=secret_name)
        return response.payload.data.decode('UTF-8')

    def get(self, variable_name, version_id='latest', direct=False):
        '''
        Get variables from Google Secret Manager if running in Google Cloud.
        If not, get from local environment file
        '''
        if not self.project_id:
            return os.getenv(variable_name)

        secret_id = os.getenv(variable_name)
        if secret_id is None and not direct:
            raise ValueError(
                f'Secret ID missing from .env file: "{variable_name}"')

        return self.__get_from_google(secret_id or variable_name, version_id)

    def create_secret_version(self, secret_id, secret_value, project_id=None):
        '''
        Create a new version of a secret in Secret Manager
        '''
        client = secretmanager.SecretManagerServiceClient()
        if not project_id:
            project_id = self.project_id
        parent = f'projects/{project_id}'

        try:
            client.create_secret(
                parent=parent,
                secret_id=secret_id,
                secret={'replication': {'automatic': {}}},
            )
        except AlreadyExists:
            pass

        response = client.add_secret_version(
            parent=f'{parent}/secrets/{secret_id}',
            payload={'data': secret_value.encode()},
        )
        return response.name
