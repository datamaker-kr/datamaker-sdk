from plugins import BasePlugin


class BaseExport(BasePlugin):

    def convert_data(self, data):
        return

    def convert_dataset(self, dataset):
        dataset_converted = []
        for data in dataset:
            dataset_converted.append(self.convert_data(data))
        return dataset_converted
