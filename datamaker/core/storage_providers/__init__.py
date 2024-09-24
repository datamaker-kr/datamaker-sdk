from abc import abstractmethod, ABC
from typing import Optional


class BaseStorageProvider(ABC):
    @property
    @abstractmethod
    def label(self):
        pass

    def __init__(self, configuration: Optional[dict] = None):
        if configuration is None:
            configuration = {}

        self.configuration = configuration

    @abstractmethod
    def get_pathlib(self):
        pass
