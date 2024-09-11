from pathlib import Path


from datamaker.core.storage_providers import BaseProvider


class FileSystemStorageProvider(BaseProvider):
    label = 'File System'
    supports_external = True

    def get_pathlib(self):
        assert 'location' in self.configuration
        return Path(self.configuration['location'])
