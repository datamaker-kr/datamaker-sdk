import os

import json
from pathlib import Path

import requests
from django.utils.translation import gettext as _
from exceptions import ClientError
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

    def get_url(self, path):
        if not path.startswith('http'):
            return os.path.join(self.base_url, path)
        return path

    def get_headers(self):
        headers = {'Authorization': f'Token {self.token}'}
        if self.workspace_code:
            headers['DATAMAKER-Workspace'] = f'Token {self.workspace_code}'
        return headers

    def set_workspace(self, code):
        self.workspace_code = code

    def request(self, method, *args, **kwargs):
        try:
            response = getattr(self.requests_session, method)(*args, **kwargs)
            if not response.ok:
                raise ClientError(
                    response.status_code,
                    response.json() if response.status_code == 400 else response.reason
                )
        except requests.ConnectionError:
            raise ClientError(408, _('서버가 응답하지 않습니다.'))
        return response.json()

    def _get(self, path, payload=None):
        url = self.get_url(path)
        headers = self.get_headers()
        return self.request('get', url, headers=headers, params=payload)

    def _post(self, path, payload=None, **kwargs):
        url = self.get_url(path)
        headers = self.get_headers()
        if 'files' in kwargs:
            kwargs['data'] = payload
        else:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(payload)
        return self.request('post', url, headers=headers, **kwargs)

    def _patch(self, path, payload=None, **kwargs):
        url = self.get_url(path)
        headers = self.get_headers()
        if 'files' in kwargs:
            kwargs['data'] = payload
        else:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(payload)
        return self.request('patch', url, headers=headers, **kwargs)

    def log(self, data):
        path = 'logs/'
        return self._post(path, payload=data)

    def get_model(self, model_id, payload=None):
        path = f'models/{model_id}/'
        return self._get(path, payload=payload)

    def create_model(self, data):
        path = 'models/'
        return self._post(path, payload=data)

    def update_model(self, code, data, files=None):
        path = f'models/{code}/'
        kwargs = {
            'payload': data
        }
        if files:
            kwargs['files'] = {}
            for name, file in files.items():
                kwargs['files'][name] = Path(file).open(mode='rb')
        return self._patch(path, **kwargs)

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

    def create_task(self, agent, task_id, service, params):
        path = 'agent_tasks/'
        payload = {
            'id': task_id,
            'agent': agent,
            'service': service,
            'params': params
        }
        return self._post(path, payload=payload)

    def create_data_file(self, file_path):
        path = 'data_files/'
        return self._post(path, files={'file': file_path.open(mode='rb')})

    def create_data_units(self, data):
        path = 'data_units/'
        return self._post(path, payload=data)

    def create_labels(self, data):
        path = 'labels/'
        return self._post(path, payload=data)

    def list_labels(self, path=None, list_all=False, payload=None):
        if not path:
            path = 'labels/'
        response = self._get(path, payload=payload)
        if list_all:
            if response['next']:
                return response['results'] + self.list_labels(
                    path=response['next'],
                    list_all=list_all,
                    payload=payload
                )
            else:
                return response['results']
        return response
