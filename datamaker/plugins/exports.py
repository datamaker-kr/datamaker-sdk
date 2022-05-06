from plugins import BasePlugin


class BaseExport(BasePlugin):

    def __init__(self, input_dataset, output_path, configuration, **kwargs):
        self.input_dataset = input_dataset
        self.output_path = output_path
        self.configuration = configuration
        super().__init__(**kwargs)

    def convert_data(self, data):
        raise NotImplementedError

    def convert_dataset(self, dataset):
        dataset_converted = []
        for data in dataset:
            dataset_converted.append(self.convert_data(data))
        return dataset_converted

    def before_convert(self, dataset):
        return dataset

    def after_convert(self, dataset):
        return dataset

    def export(self):
        dataset = self.before_convert(self.input_dataset)
        dataset = self.convert_data(dataset)
        dataset = self.after_convert(dataset)
        return dataset
