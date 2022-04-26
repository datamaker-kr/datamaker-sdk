from . import BasePlugin


class BasePreprocessor(BasePlugin):
    params_serializer_class = None
    params = None

    def __init__(self, *args, **kwargs):
        self.params = kwargs.pop('params', {})
        super().__init__(*args, **kwargs)

    def is_valid(self):
        serializer = self.params_serializer_class(data=self.params)
        return serializer.is_valid()

    def preprocess(self, *args, **kwargs):
        raise NotImplementedError
