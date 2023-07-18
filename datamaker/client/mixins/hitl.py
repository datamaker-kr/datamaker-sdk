class HITLClientMixin:
    def get_assignment(self, pk):
        path = f'assignments/{pk}/'
        return self._get(path)

    def list_assignments(self, payload=None):
        path = 'assignments/'
        return self._list(path, payload)
