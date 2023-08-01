import copy
from pathlib import Path

from django.utils.translation import gettext as _
from django_lock import lock

from . import BasePlugin
from ..utils.file import download_file, files_url_to_path

LOADED_MODELS = {}


class BaseNet(BasePlugin):
    # TODO implement specifying which hardware to use (gpu-n, cpu)
    """
    input_dataset_conversion = {
        "plugin": "coco",
        "configuration": {}
    }
    """

    # attributes to override
    input_dataset_conversion = None
    input_schema = None

    # attributes for internal use
    model = None
    count_iterations = None
    export_plugin_class = None

    def __init__(self, export_plugin_class=None, **kwargs):
        self.export_plugin_class = export_plugin_class
        super().__init__(**kwargs)

    def set_model(self, model):
        self.model = model

    def get_loaded_model(self):
        with lock(f'model_load_{self.model["id"]}'):
            if self.model['id'] not in LOADED_MODELS:
                LOADED_MODELS[self.model['id']] = self.load_model()
        return LOADED_MODELS[self.model['id']]

    def get_model_base_path(self):
        return self.base_path / Path(f'model_{self.model["id"]}')

    def download_dataset(self, input_dataset, download_path_map):
        base_path = self.get_model_base_path()

        for input_data in input_dataset:
            for name, url in input_data['files'].items():
                path_download = base_path / download_path_map[name]
                path_download.mkdir(parents=True, exist_ok=True)
                download_file(url, path_download, name=str(input_data['id']))

    def get_input_dataset_for_training(self, model_id):
        """
        :param model_id:
        :return:
        {
            "train": [
                {
                    "files": {
                        "image": {
                            "path": "/path/to/image.jpg",
                            "meta": {
                                "width": 265,
                                "height": 190,
                                "created": 1651563526.0277045,
                                "file_size": 5191,
                                "last_modified": 1651563526.0277045
                            }
                        }
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
        """
        client = self.logger.client
        assert bool(client)

        category_int_to_str = {1: 'train', 2: 'validation', 3: 'test'}
        input_dataset = {}

        train_dataset, count_dataset = client.list_train_dataset(
            payload={
                'fields': ['category', 'files', 'ground_truth'],
                'model': model_id,
            },
            list_all=True,
        )

        for i, train_data in enumerate(train_dataset, start=1):
            self.set_progress(i, count_dataset, category='dataset_download')
            category = category_int_to_str[train_data.pop('category')]
            try:
                input_dataset[category].append(train_data)
            except KeyError:
                input_dataset[category] = [train_data]

        return input_dataset

    def convert_dataset(self, model, input_dataset):
        client = self.logger.client
        assert bool(client)

        input_dataset_converted = {}
        project = client.get_project(model['configuration']['dataset']['project'])
        try:
            classification = project['configuration']['classification']
        except KeyError:
            classification = None

        for category, dataset in input_dataset.items():
            configuration = copy.deepcopy(
                self.input_dataset_conversion['configuration']
            )
            configuration.update(
                {
                    'name': category,
                    'classification': classification,
                    'export_root': str(self.get_model_base_path()),
                }
            )
            export_plugin = self.export_plugin_class(
                dataset,
                len(dataset),
                configuration,
                logger=self.logger,
                progress_prefix=category,
            )
            input_dataset_converted[category] = export_plugin.export()

        return input_dataset_converted

    def run_train(self, model, **kwargs):
        client = self.logger.client
        assert bool(client)

        self.count_iterations = model['configuration']['hyperparameter']['iterations']

        # download dataset
        self.log_message(_('학습 데이터셋 준비를 시작합니다.'))
        input_dataset = self.get_input_dataset_for_training(model['id'])

        # convert dataset
        self.log_message(_('학습 데이터셋 포맷 변환을 시작합니다.'))
        if self.input_dataset_conversion:
            input_dataset = self.convert_dataset(model, input_dataset)

        # train dataset
        client.update_model(model['id'], {'status': 2})
        self.log_message(_('모델 학습을 시작합니다.'))
        model_files = self.train(
            input_dataset,
            model['configuration']['hyperparameter'],
            checkpoint=model['parent'],
        )

        # upload model_data
        self.log_message(_('학습된 모델을 업로드 합니다.'))
        client.update_model(model['id'], {'status': 3}, files=model_files)

        self.end_log()
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
        raise NotImplementedError

    def test(self, ground_truth, prediction):
        raise NotImplementedError

    def infer(self, model, input_data):
        raise NotImplementedError

    def log_iteration(self, i, **kwargs):
        self.log('iteration', {'iteration': i, **kwargs})
        self.set_progress(i, self.count_iterations, category='iteration')
