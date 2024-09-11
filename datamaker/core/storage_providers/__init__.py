from abc import ABCMeta
from typing import Optional


class BaseProvider(metaclass=ABCMeta):
    def __init__(self, configuration: Optional[dict] = None):
        if configuration is None:
            configuration = {}

        self.configuration = configuration

    def get_pathlib(self):
        raise NotImplementedError
