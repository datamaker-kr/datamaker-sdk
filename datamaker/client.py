import os

import json
import requests


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
        if response.status_code != requests.codes.ok:
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
        path = 'datasets'
        return self._get(path)
