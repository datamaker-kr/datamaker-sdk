class AnnotationClientMixin:

    def list_labels(self, payload=None, list_all=False):
        path = 'labels/'
        return self._list(path, payload, list_all)

    def create_labels(self, data):
        path = 'labels/'
        return self._post(path, payload=data)
