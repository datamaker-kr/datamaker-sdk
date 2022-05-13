import json
from pathlib import Path

from constance import config

from ..utils.file import json_default
from . import BasePlugin


class BaseExport(BasePlugin):
    input_dataset = None
    count_dataset = None
    configuration = None

    def __init__(self, input_dataset, count_dataset, configuration, **kwargs):
        super().__init__(**kwargs)
        self.input_dataset = input_dataset
        self.count_dataset = count_dataset
        self.configuration = configuration

        export_root = configuration.get('export_root', config.EXPORT_ROOT)
        self.base_path = Path(export_root) / configuration['name']
        self.base_path.mkdir(parents=True)

    def get_classification(self):
        return self.configuration['classification']

    def convert_data(self, data):
        raise NotImplementedError

    def convert_dataset(self, dataset):
        dataset_converted = []
        for i, data in enumerate(dataset, start=1):
            self.set_progress(i, self.count_dataset, category='dataset_conversion')
            dataset_converted.append(self.convert_data(data))
        return dataset_converted

    def before_convert(self, dataset):
        return dataset

    def after_convert(self, dataset):
        return dataset

    def export(self):
        dataset = self.before_convert(self.input_dataset)
        dataset = self.convert_dataset(dataset)
        dataset = self.after_convert(dataset)
        return dataset

    def save_as_json(self, name, dataset):
        path = self.base_path / name
        with path.open('w') as f:
            json.dump(dataset, f, indent=4, ensure_ascii=False, default=json_default)
        return str(path)
