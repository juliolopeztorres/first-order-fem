import abc
from typing import Any


class UiLoaderServiceInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(self, uiFileName: str) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def getAnimationPath(self, fileName: str) -> Any:
        raise NotImplementedError
