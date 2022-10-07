import abc

from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface


class ProgressBarViewInterface(ViewInterface):
    @abc.abstractmethod
    def show(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def setProgress(self, progress: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def resetText(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def showText(self, text: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def getText(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def getProgress(self) -> int:
        raise NotImplementedError
