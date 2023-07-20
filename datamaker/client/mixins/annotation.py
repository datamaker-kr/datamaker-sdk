from ..utils import get_default_url_conversion


class AnnotationClientMixin:
    def get_project(self, pk):
        path = f'projects/{pk}/'
        return self._get(path)

    def get_label_tag(self, pk):
        path = f'label_tags/{pk}/'
        return self._get(path)

    def list_label_tags(self, payload=None):
        path = 'label_tags/'
        return self._list(path, payload)

    def list_labels(self, payload=None, url_conversion=None, list_all=False):
        path = 'labels/'
        url_conversion = get_default_url_conversion(
            url_conversion, files_fields=['files']
        )
        return self._list(path, payload, url_conversion, list_all)

    def create_labels(self, data):
        path = 'labels/'
        return self._post(path, payload=data)

    def create_label_tags(self, data):
        path = 'label_tags/'
        return self._post(path, payload=data)

    def set_tags_labels(self, data, params=None):
        path = 'labels/set_tags/'
        return self._post(path, payload=data, params=params)
