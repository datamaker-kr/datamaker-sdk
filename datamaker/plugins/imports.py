from datamaker.client import ClientError
from datamaker.plugins import BasePlugin


class BaseImport(BasePlugin):
    def __init__(
        self,
        category,
        target_id,
        storage,
        paths,
        configuration,
        batch_size,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.category = category
        self.target_id = target_id
        self.storage = storage
        self.paths = paths
        self.configuration = configuration
        self.batch_size = batch_size

    def prepare_dataset(self, storage, paths, allowed_extensions, configuration):
        raise NotImplementedError

    def import_dataset(self):
        if self.category == 'project':
            dataset_id = self.logger.client.get_project(self.target_id)['dataset']
            dataset = self.logger.client.get_dataset(dataset_id)
        else:
            dataset_id = self.target_id
            dataset = self.logger.client.get_dataset(self.target_id)

        allowed_extensions = {}
        import_file_names = {
            data['file_type']: data['name'] for data in dataset['file_specifications']
        }
        for key, extensions in dataset['allowed_extensions'].items():
            new_key = import_file_names.get(key)
            allowed_extensions[new_key] = extensions

        configuration = self.configuration

        dataset = self.prepare_dataset(
            self.storage, self.paths, allowed_extensions, configuration
        )
        try:
            if self.category == 'project':
                self.logger.client.import_dataset(
                    dataset_id,
                    dataset,
                    project_id=self.target_id,
                    batch_size=self.batch_size,
                )
            else:
                self.logger.client.import_dataset(
                    dataset_id,
                    dataset,
                    batch_size=self.batch_size,
                )
        except ClientError as e:
            raise e
