from datamaker.client import ClientError
from datamaker.plugins import BasePlugin


class BaseImport(BasePlugin):
    def get_files(self, storage, paths, allowed_extensions, configuration):
        raise NotImplementedError

    def prepare_dataset(self, storage, paths, allowed_extensions, configuration):
        raise NotImplementedError

    def import_dataset(self, project, storage, paths, allowed_extensions, **kwargs):
        batch_size = kwargs.get('batch_size', 500)
        project_id = project['id']
        dataset_id = project['dataset']
        configuration = kwargs['configuration']

        response = {'status': 'success'}

        dataset = self.prepare_dataset(
            storage, paths, allowed_extensions, configuration
        )
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
