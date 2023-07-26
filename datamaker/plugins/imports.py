from pathlib import Path

from datamaker.client import DatasetClientMixin

from datamaker.plugins import BasePlugin


class BaseImport(BasePlugin):
    def __init__(self, dataset_id, project_id, storage_id, storage_path, allowed_extensions, **kwargs):
        super().__init__(**kwargs)
        self.dataset_id = dataset_id
        self.project_id = project_id
        self.storage_id = storage_id
        self.storage_path = storage_path
        self.allowed_extensions = allowed_extensions
        self.groups = kwargs['groups']
        self.batch_size = 500 if not kwargs['batch_size'] else kwargs['batch_size']

    # TODO 나중에는 get_pathlib 통해서 가져올 것, 현재는 /mnt/projects/에서 가져온다 가정
    def get_files(self):
        files = {}
        for allowed_extension in self.allowed_extensions:
            for file_type, extensions in allowed_extension.items():
                files[file_type] = []
                for extension in extensions:
                    paths_image = Path(f'/mnt/projects/{self.storage_path}').rglob(f'*.{extension}')
                    for index, path in enumerate(paths_image):
                        if path.parent.name == '@eaDir' or path.parent.parent.name == '@eaDir':
                            continue

                        files[file_type].append(path)
        return files

    def prepare_dataset(self):
        files = self.get_files()
        dataset = []
        keys = list(files.keys())

        for i in range(len(files[keys[0]])):
            files_entry = {key: files[key][i] for key in keys}

            if self.groups:
                entry = {
                    'files': files_entry,
                    'groups': self.groups
                }
            else:
                entry = {
                    'files': files_entry
                }
            dataset.append(entry)

        return dataset

    def import_dataset(self):
        dataset = self.prepare_dataset()
        DatasetClientMixin.import_dataset(
            self.dataset_id,
            dataset,
            project_id=self.project_id,
            batch_size=self.batch_size
        )
