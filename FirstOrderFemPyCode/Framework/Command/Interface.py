import abc
from typing import Any, Dict, Tuple


class CommandInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def GetResources(self) -> Dict[str, str]:
        raise NotImplementedError

    @abc.abstractmethod
    def IsActive(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def Activated(self) -> None:
        raise NotImplementedError


class DataContainerInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def onDocumentRestored(self, obj: Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self, obj: Any) -> None:
        raise NotImplementedError


class ViewObjectInterface:
    class ObjectInterface:
        Name: str
        Label: str
        Document: Any
        ViewObject: Any # Valid ViewObjectInterface instance. `Any` for further casting
        Proxy: Any # Valid DataContainerInterface instance. `Any` for further casting

    Proxy: Any # Valid ViewProviderInterface instance. `Any` for further casting
    Object: ObjectInterface
    ShapeColor: Tuple
    Transparency: int
    Visibility: bool


class ViewProviderInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getIcon(self) -> str:
        raise NotImplementedError

    # `viewObject` should be a valid instance of `ViewObjectInterface` or subclass
    @abc.abstractmethod
    def attach(self, viewObject: Any) -> None:
        raise NotImplementedError

    # `viewObject` should be a valid instance of `ViewObjectInterface` or subclass
    @abc.abstractmethod
    def doubleClicked(self, viewObject: Any) -> bool:
        raise NotImplementedError

    # `viewObject` should be a valid instance of `ViewObjectInterface` or subclass
    @abc.abstractmethod
    def setEdit(self, viewObject: Any, mode: int) -> bool:
        raise NotImplementedError

    # `viewObject` should be a valid instance of `ViewObjectInterface` or subclass
    @abc.abstractmethod
    def unsetEdit(self, viewObject: Any, mode: int) -> None:
        raise NotImplementedError

    # `viewObject` should be a valid instance of `ViewObjectInterface` or subclass
    def onDelete(self, viewObject: Any, mode: int) -> bool:
        return True

    def __getstate__(self) -> None:
        pass

    def __setstate__(self, state: Any) -> None:
        pass
    
    # `dataObject` should be a valid instance of `ViewObjectInterface.ObjectInterface` or subclass
    def updateData(self, dataObject: Any, prop: str):
        if prop == 'Label':
            self.onLabelChanged(dataObject)

    # `viewObject` should be a valid instance of `ViewObjectInterface` or subclass
    def onChanged(self, viewObject: Any, prop: Any) -> None:
        if prop == 'Visibility':
            self.onVisibilityChanged(viewObject)

    # `viewObject` should be a valid instance of `ViewObjectInterface` or subclass
    def onVisibilityChanged(self, viewObject: Any) -> None:
        pass

    # `viewObject` should be a valid instance of `ViewObjectInterface` or subclass
    def onLabelChanged(self, dataObject: Any) -> None:
        pass
