import boto3
import s3path

from datamaker.core.storage_providers import BaseProvider


class AmazonS3StorageProvider(BaseProvider):
    label = 'Amazon S3'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.s3_init = False

    def _get_s3_path(self):
        if not self.s3_init:
            boto3_configs = {
                'aws_access_key_id': self.configuration['access_key'],
                'aws_secret_access_key': self.configuration['secret_key'],
                'region_name': self.configuration['region_name'],
            }
            boto3.setup_default_session(**boto3_configs)
            self.s3_init = True
        return s3path.S3Path('/' + self.configuration['bucket_name'])

    def get_pathlib(self):
        pathlib_object = self._get_s3_path()
        return pathlib_object
