class MLClientMixin:

    def get_model(self, pk, payload=None):
        path = f'models/{pk}/'
        return self._get(path, payload=payload)

    def create_model(self, data):
        path = 'models/'
        return self._post(path, payload=data)

    def update_model(self, pk, data, files=None):
        path = f'models/{pk}/'
        return self._patch(path, payload=data, files=files)

    def list_train_dataset(self, payload=None, list_all=False):
        path = 'train_dataset/'
        return self._list(path, payload, list_all)
