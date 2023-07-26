from copy import deepcopy
from multiprocessing import Pool

from tqdm import tqdm
from ..utils import get_batched_list


class DatasetClientMixin:
    def list_dataset(self):
        path = 'datasets/'
        return self._get(path)

    def get_dataset(self, pk):
        path = f'datasets/{pk}/'
        return self._get(path)

    def create_data_file(self, file_path):
        path = 'data_files/'
        return self._post(path, files={'file': file_path})

    def create_data_units(self, data):
        path = 'data_units/'
        return self._post(path, payload=data)

    def create_data_unit_files(self, data):
        path = 'data_unit_files/'
        return self._post(path, payload=data)

    def import_dataset(
        self, dataset_id, dataset, project_id=None, batch_size=1000, process_pool=10
    ):
        # TODO validate datset with schema

        params = [(data, dataset_id) for data in dataset]

        with Pool(processes=process_pool) as pool:
            dataset = pool.starmap(self.import_data_file, tqdm(params))

        batches = get_batched_list(dataset, batch_size)

        for batch in tqdm(batches):
            batch_sequential = []

            for data in batch:
                data_sequential = {}
                names_to_remove = []
                max_index = None

                for name, file in data['files'].items():
                    if isinstance(file, list):
                        data_sequential[name] = file
                        names_to_remove.append(name)
                        if max_index is None:
                            max_index = len(file)
                        else:
                            assert max_index == len(
                                file
                            ), 'The number of files must be the same.'

                for name in names_to_remove:
                    del data['files'][name]

                if data_sequential:
                    try:
                        data['meta']['max_index'] = max_index
                    except KeyError:
                        data['meta'] = {'max_index': max_index}
                    batch_sequential.append(data_sequential)

            data_units = self.create_data_units(batch)

            if batch_sequential:
                for data, data_unit in zip(batch_sequential, data_units):
                    for name, files in data.items():
                        self.create_data_unit_files(
                            {
                                'data_unit': data_unit['id'],
                                'name': name,
                                'files': files,
                            }
                        )

            if project_id:
                labels_data = []
                for data, data_unit in zip(batch, data_units):
                    label_data = {
                        'project': project_id,
                        'data_unit': data_unit['id'],
                    }
                    if 'ground_truth' in data:
                        label_data['ground_truth'] = data['ground_truth']

                    labels_data.append(label_data)

                self.create_labels(labels_data)

    def import_data_file(self, data, dataset_id):
        result = deepcopy(data)
        for name, path_or_paths in data['files'].items():
            if isinstance(path_or_paths, list):
                paths = path_or_paths
                result['files'][name] = []
                for i, path in enumerate(paths, start=1):
                    data_file = self.create_data_file(path)
                    file = {
                        'checksum': data_file['checksum'],
                        'path': str(path),
                        'index': i,
                    }
                    result['files'][name].append(file)
            else:
                path = path_or_paths
                data_file = self.create_data_file(path)
                result['dataset'] = dataset_id
                result['files'][name] = {
                    'checksum': data_file['checksum'],
                    'path': str(path),
                }
        return result
