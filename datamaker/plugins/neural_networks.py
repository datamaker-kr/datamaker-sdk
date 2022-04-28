from pathlib import Path

from django_lock import lock

from . import BasePlugin
from ..utils.file import download_file, files_url_to_path

LOADED_MODELS = {}


class BaseNet(BasePlugin):
    model = None
    input_schema = None

    # def get_device(self, ):
    #    raise

    def set_model(self, model):
        self.model = model

    def get_loaded_model(self):
        with lock(f'model_load_{self.model["code"]}'):
            if self.model['code'] not in LOADED_MODELS:
                LOADED_MODELS[self.model['code']] = self.load_model()
        return LOADED_MODELS[self.model['code']]

    def get_model_base_path(self, train=False):
        if train:
            return self.base_path
        else:
            return self.base_path / Path(self.model['code'])

    def download_dataset(self, input_dataset, download_path_map, train=False):
        base_path = self.get_model_base_path(train=train)

        for input_data in input_dataset:
            for name, url in input_data['files'].items():
                path_download = base_path / download_path_map[name]
                path_download.mkdir(parents=True, exist_ok=True)
                download_file(url, path_download, name=str(input_data['id']))

    def infer_many(self, input_dataset):
        for input_data in input_dataset:
            files_url_to_path(input_data['files'])
        return [self.infer(input_data) for input_data in input_dataset]

    def load_model(self):
        raise NotImplementedError

    def train(self, input_dataset, configuration):
        raise NotImplementedError

    def test(self, input_dataset):
        raise NotImplementedError

    def infer(self, input_data):
        raise NotImplementedError

    def log_iteration(self, epoch, i, **kwargs):
        self.log('iteration', {'epoch': epoch, 'iteration': i, **kwargs})
