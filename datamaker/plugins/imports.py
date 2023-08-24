from pathlib import Path

from datamaker.plugins import BasePlugin


class BaseImport(BasePlugin):
    def __init__(
        self,
        category,
        target_id,
        storage_id,
        paths,
        configuration,
        batch_size=500,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.client = self.logger.client
        assert bool(self.client)

        self.category = category
        self.target_id = target_id
        self.storage_id = storage_id
        self.paths = paths
        self.configuration = configuration
        self.batch_size = batch_size

    def prepare_dataset(self, storage, paths, allowed_extensions, configuration):
        raise NotImplementedError

    def import_dataset(self):
        if self.category == 'project':
            project_id = self.target_id
            dataset_id = self.client.get_project(project_id)['dataset']
        else:
            project_id = None
            dataset_id = self.target_id

        dataset = self.client.get_dataset(dataset_id)
        storage = self.get_storage()
        allowed_extensions = dataset['allowed_extensions']

        dataset = self.prepare_dataset(
            storage, self.paths, allowed_extensions, self.configuration
        )
        self.client.import_dataset(
            dataset_id,
            dataset,
            project_id=project_id,
            batch_size=self.batch_size,
        )

    def get_storage(self):
        # TODO support multiple storages
        class FileSystemStorage:
            def __init__(self, location):
                self.location = location

            def get_pathlib(self):
                return Path(self.location)

        storage = self.client.get_storage(self.storage_id)
        assert (
            storage['provider'] == 'file_system'
            and 'location' in storage['configuration']
        )
        return FileSystemStorage(storage['configuration']['location'])
