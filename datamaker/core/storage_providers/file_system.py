from pathlib import Path


from datamaker.core.storage_providers import BaseStorageProvider


class FileSystemStorageStorageProvider(BaseStorageProvider):
    label = 'File System'

    def get_pathlib(self):
        assert 'location' in self.configuration
        return Path(self.configuration['location'])
