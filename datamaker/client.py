import os

import json
from pathlib import Path

import requests
from tqdm import tqdm


class Client:
    base_url = None
    token = None
    workspace_code = None

    def __init__(self, base_url, token, workspace_code=None):
        self.base_url = base_url
        self.token = token
        if workspace_code:
            self.set_workspace(workspace_code)
        requests_session = requests.Session()
        self.requests_session = requests_session

    @staticmethod
    def get_response(response):
        if not response.ok:
            if 400 <= response.status_code < 500:
                raise requests.HTTPError(response.status_code, response.reason, response.json())
            else:
                raise requests.HTTPError(response.status_code, response.reason)
        return response.json()

    def get_url(self, path):
        return os.path.join(self.base_url, path)

    def get_headers(self):
        headers = {'Authorization': f'Token {self.token}'}
        if self.workspace_code:
            headers['DATAMAKER-Workspace'] = f'Token {self.workspace_code}'
        return headers

    def set_workspace(self, code):
        self.workspace_code = code

    def _get(self, path, payload=None):
        url = self.get_url(path)
        headers = self.get_headers()
        response = self.requests_session.get(
            url, headers=headers, params=payload
        )
        return self.get_response(response)

    def _post(self, path, payload=None):
        url = self.get_url(path)
        headers = self.get_headers()
        headers['Content-Type'] = 'application/json'
        response = self.requests_session.post(
            url, headers=headers, data=json.dumps(payload)
        )
        return self.get_response(response)

    def _patch(self, path, payload=None):
        url = self.get_url(path)
        headers = self.get_headers()
        headers['Content-Type'] = 'application/json'
        response = self.requests_session.patch(
            url, headers=headers, data=json.dumps(payload)
        )
        return self.get_response(response)

    def list_dataset(self):
        path = 'datasets/'
        return self._get(path)

    def import_dataset(self, dataset_id, dataset, project_id=None):

        # TODO validate datset with schema

        for data in tqdm(dataset):
            for name, path in data['files'].items():
                data_file = self.create_data_file(path)
                data['dataset'] = dataset_id
                data['files'][name] = {
                    'checksum': data_file['checksum'],
                    'path': str(path)
                }

        data_units = self.create_data_units(dataset)

        if project_id:
            labels_data = []
            for data, data_unit in zip(dataset, data_units):
                label_data = {
                  'project': project_id,
                  'data_unit': data_unit['id']
                }
                if 'ground_truth' in data:
                    label_data['ground_truth'] = data['ground_truth']

                labels_data.append(label_data)

            self.create_labels(labels_data)

    def create_data_file(self, file_path):
        path = 'data_files/'
        url = self.get_url(path)
        headers = self.get_headers()
        response = self.requests_session.post(
            url, headers=headers, files={'file': file_path.open(mode='rb')}
        )
        return self.get_response(response)

    def create_data_units(self, data):
        path = 'data_units/'
        return self._post(path, payload=data)

    def create_labels(self, data):
        path = 'labels/'
        return self._post(path, payload=data)
