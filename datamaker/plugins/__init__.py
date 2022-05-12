from pathlib import Path

from constance import config
from django.utils.translation import gettext as _
from nanoid import generate

from datamaker.utils.logger import Logger


class BasePlugin:
    base_path = None
    logger = None
    progress_prefix = ''

    def __init__(self, logger=None, progress_prefix=None):
        self.base_path = Path(config.TEMP_ROOT) / 'service_executions' / generate()
        if progress_prefix:
            self.progress_prefix = progress_prefix

        if logger:
            self.logger = logger
        else:
            self.logger = Logger()

    def set_progress(self, current, total, category=''):
        if self.progress_prefix:
            category = f'{self.progress_prefix}_{category}'
        self.logger.set_progress(current, total, category)

    def log(self, action, data):
        self.logger.log(action, data)

    def log_message(self, message):
        self.logger.log('message', {'content': message})

    def end_log(self):
        self.log_message(_('작업이 완료되었습니다.'))
