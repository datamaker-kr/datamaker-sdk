from pathlib import Path

from nanoid import generate

from datamaker.utils.logger import Logger


class BasePlugin:
    base_path = None
    logger = None

    def __init__(self, logger=None):
        self.base_path = Path('/tmp/agent') / generate()

        if logger:
            self.logger = logger
        else:
            self.logger = Logger()

    def set_progress(self, current, total, category=''):
        self.logger.set_progress(current, total, category)

    def log(self, action, data):
        self.logger.log(action, data)

    def log_message(self, message):
        self.logger.log('message', {'content': message})
