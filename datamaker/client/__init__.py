import os
import json
from pathlib import Path

import requests

from django.utils.translation import gettext as _

from .exceptions import ClientError
from .mixins.annotation import AnnotationClientMixin
from .mixins.dataset import DatasetClientMixin
from .mixins.integration import IntegrationClientMixin
from .mixins.ml import MLClientMixin

mixins = (
    AnnotationClientMixin,
    DatasetClientMixin,
    IntegrationClientMixin,
    MLClientMixin,
)


class Client(*mixins):
    base_url = None
    token = None
    workspace_code = None

    def __init__(self, base_url, token, workspace_code=None):
        self.base_url = base_url
        self.token = token
        if workspace_code:
            self.workspace_code = workspace_code
        requests_session = requests.Session()
        self.requests_session = requests_session

    def _get_url(self, path):
        if not path.startswith(self.base_url):
            return os.path.join(self.base_url, path)
        return path

    def _get_headers(self):
        headers = {'Authorization': f'Token {self.token}'}
        if self.workspace_code:
            headers['DATAMAKER-Workspace'] = f'Token {self.workspace_code}'
        return headers

    def _request(self, method, path, **kwargs):
        url = self._get_url(path)
        headers = self._get_headers()

        if method in ['post', 'put', 'patch']:
            if 'files' in kwargs:
                for name, file in kwargs['files'].items():
                    kwargs['files'][name] = Path(str(file)).open(mode='rb')
            else:
                headers['Content-Type'] = 'application/json'
                if 'data' in kwargs:
                    kwargs['data'] = json.dumps(kwargs['data'])

        try:
            response = getattr(self.requests_session, method)(url, headers=headers, **kwargs)
            if not response.ok:
                raise ClientError(
                    response.status_code,
                    response.json() if response.status_code == 400 else response.reason
                )
        except requests.ConnectionError:
            raise ClientError(408, _('서버가 응답하지 않습니다.'))

        return response.json()

    def _get(self, path, payload=None):
        return self._request('get', path, params=payload)

    def _post(self, path, payload=None, files=None):
        return self._request('post', path, data=payload, files=files)

    def _patch(self, path, payload=None, files=None):
        return self._request('patch', path, data=payload, files=files)

    def _list(self, path, payload=None, list_all=False):
        response = self._get(path, payload=payload)
        if list_all:
            yield from response['results']
            if response['next']:
                yield from self._list(response['next'], payload=payload, list_all=list_all)
        else:
            return response
