from tqdm import tqdm
from ..utils import get_batched_list


class DatasetClientMixin:

    def list_dataset(self):
        path = 'datasets/'
        return self._get(path)

    def create_data_file(self, file_path):
        path = 'data_files/'
        return self._post(path, files={'file': file_path})

    def create_data_units(self, data):
        path = 'data_units/'
        return self._post(path, payload=data)

    def import_dataset(self, dataset_id, dataset, project_id=None, batch_size=1000):

        # TODO validate datset with schema

        for data in tqdm(dataset):
            for name, path in data['files'].items():
                data_file = self.create_data_file(path)
                data['dataset'] = dataset_id
                data['files'][name] = {
                    'checksum': data_file['checksum'],
                    'path': str(path)
                }

        batches = get_batched_list(dataset, batch_size)

        for batch in batches:
            data_units = self.create_data_units(batch)

            if project_id:
                labels_data = []
                for data, data_unit in zip(batch, data_units):
                    label_data = {
                        'project': project_id,
                        'data_unit': data_unit['id']
                    }
                    if 'ground_truth' in data:
                        label_data['ground_truth'] = data['ground_truth']

                    labels_data.append(label_data)

                self.create_labels(labels_data)
