from pathlib import Path

from django.utils.translation import gettext as _
from django_lock import lock

from . import BasePlugin
from ..utils.file import download_file, files_url_to_path

LOADED_MODELS = {}


class BaseNet(BasePlugin):
    # TODO implement specifying which hardware to use (gpu-n, cpu)

    model = None
    input_schema = None
    count_iterations = None

    def set_model(self, model):
        self.model = model

    def get_loaded_model(self):
        with lock(f'model_load_{self.model["code"]}'):
            if self.model['code'] not in LOADED_MODELS:
                LOADED_MODELS[self.model['code']] = self.load_model()
        return LOADED_MODELS[self.model['code']]

    def get_model_base_path(self):
        return self.base_path / Path(self.model['code'])

    def download_dataset(self, input_dataset, download_path_map):
        base_path = self.get_model_base_path()

        for input_data in input_dataset:
            for name, url in input_data['files'].items():
                path_download = base_path / download_path_map[name]
                path_download.mkdir(parents=True, exist_ok=True)
                download_file(url, path_download, name=str(input_data['id']))

    def get_input_dataset_for_training(self, model_code):
        client = self.logger.client
        assert bool(client)

        category_int_to_str = {1: 'train', 2: 'validation', 3: 'test'}
        input_dataset = {'train': [], 'validation': [], 'test': []}

        train_dataset, count_dataset = client.list_train_dataset(
            payload={
                'fields': ['category', 'files', 'ground_truth'],
                'model': model_code
            },
            list_all=True
        )

        for i, train_data in enumerate(train_dataset, start=1):
            self.set_progress(i, count_dataset, category='dataset_download')
            category = category_int_to_str[train_data.pop('category')]
            input_dataset[category].append(train_data)

        return input_dataset

    def run_train(self, model, **kwargs):
        client = self.logger.client
        assert bool(client)

        self.count_iterations = model['configuration']['hyperparameter']['iterations']

        # download dataset
        self.log_message(_('학습 데이터셋 준비를 시작합니다.'))
        input_dataset = self.get_input_dataset_for_training(model['code'])

        # convert dataset

        # train dataset
        client.update_model(model['code'], {'status': 2})
        self.log_message(_('모델 학습을 시작합니다.'))
        model_files = self.train(
            input_dataset, model['configuration']['hyperparameter'],
            checkpoint=model['parent']
        )

        # upload model_data
        self.log_message(_('학습된 모델을 업로드 합니다.'))
        client.update_model(model['code'], {'status': 3}, files=model_files)

        return {}

    def run_test(self, input_dataset, **kwargs):
        predictions = self.run_infer(input_dataset, **kwargs)
        results = [
            self.test(input_data['ground_truth'], prediction)
            for input_data, prediction in zip(input_dataset, predictions)
        ]
        summary = {}

        for result in results:
            for key, value in result.items():
                try:
                    summary[key] += value
                except KeyError:
                    summary[key] = value

        count_results = len(results)
        for key, value in summary.items():
            summary[key] = value / count_results

        return summary

    def run_infer(self, input_dataset, **kwargs):
        model = self.get_loaded_model()
        for input_data in input_dataset:
            files_url_to_path(input_data['files'])
        return [self.infer(model, input_data) for input_data in input_dataset]

    def load_model(self):
        raise NotImplementedError

    def train(self, input_dataset, hyperparameter, checkpoint=None):
        """
        :param input_dataset:
        {
            "train": [
                {
                    "files": {
                        "image": "/path/to/image.jpg"
                    },
                    "ground_truth": {
                        ...label_data
                    }
                },
                ...
            ],
            "validation": ...,
            "test": ...
        }
        :param hyperparameter:
        :param checkpoint:
        :return:
        """
        raise NotImplementedError

    def test(self, ground_truth, prediction):
        raise NotImplementedError

    def infer(self, model, input_data):
        raise NotImplementedError

    def log_iteration(self, i, **kwargs):
        self.log('iteration', {'iteration': i, **kwargs})
        self.set_progress(i, self.count_iterations, category='iteration')
