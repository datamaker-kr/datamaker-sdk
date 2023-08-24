class IntegrationClientMixin:
    def get_plugin(self, pk):
        path = f'plugins/{pk}/'
        return self._get(path)

    def create_logs(self, data):
        path = 'logs/'
        return self._post(path, payload=data)

    def create_task(self, data):
        path = 'tasks/'
        return self._post(path, payload=data)

    def update_task(self, pk, data):
        path = f'tasks/{pk}/'
        return self._patch(path, payload=data)

    def get_storage(self, pk, params=None):
        path = f'storages/{pk}/'
        return self._get(path, payload=params)
