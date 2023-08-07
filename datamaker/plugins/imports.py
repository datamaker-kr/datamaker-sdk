from datamaker.client import ClientError
from datamaker.plugins import BasePlugin


class BaseImport(BasePlugin):
    def get_files(self, allowed_extensions, paths):
        raise NotImplementedError

    def prepare_dataset(self, storage, paths, **kwargs):
        raise NotImplementedError

    def import_dataset(self, project, storage, paths, **kwargs):
        batch_size = kwargs.get('batch_size', 500)
        project_id = project['id']
        dataset_id = project['dataset']

        response = {'status': 'success'}
        dataset = self.prepare_dataset(storage, paths, **kwargs)
        try:
            self.logger.client.import_dataset(
                dataset_id,
                dataset,
                project_id=project_id,
                batch_size=batch_size,
            )
        except ClientError as e:
            response['status'] = str(e)

        return response
