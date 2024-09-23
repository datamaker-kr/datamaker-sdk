from s3path import register_configuration_parameter, PureS3Path

from datamaker.core.storage_providers import BaseStorageProvider
import boto3
import s3path


class AmazonS3StorageProvider(BaseStorageProvider):
    label = 'Amazon S3'

    def get_pathlib(self):
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=self.configuration['access_key'],
            aws_secret_access_key=self.configuration['secret_key'],
            region_name=self.configuration['region_name'],
        )

        bucket_name = self.configuration['bucket_name']
        register_configuration_parameter(
            PureS3Path(f'/{bucket_name}'), resource=s3_resource
        )

        return s3path.S3Path(f'/{bucket_name}')
