class HITLClientMixin:
    def get_assignment(self, pk):
        path = f'assignments/{pk}/'
        return self._get(path)

    def list_assignments(self, payload=None):
        path = 'assignments/'
        return self._list(path, payload)

    def set_tags_assignments(self, data, params=None):
        path = 'assignments/set_tags/'
        return self._post(path, payload=data, params=params)
