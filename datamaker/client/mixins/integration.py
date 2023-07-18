class IntegrationClientMixin:
    def get_plugin(self, pk):
        path = f'plugins/{pk}/'
        return self._get(path)

    def create_logs(self, data):
        path = 'logs/'
        return self._post(path, payload=data)

    def create_task(self, data):
        path = 'agent_tasks/'
        return self._post(path, payload=data)
