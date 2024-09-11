from abc import ABCMeta, abstractmethod
from typing import Optional


class BaseProvider(metaclass=ABCMeta):
    @property
    @abstractmethod
    def label(self):
        pass

    def __init__(self, configuration: Optional[dict] = None):
        if configuration is None:
            configuration = {}

        self.configuration = configuration

    def get_pathlib(self):
        raise NotImplementedError
