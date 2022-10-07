import abc
from typing import Any
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface

class TaskPanelSimulationContainerPropertiesViewInterface(ViewInterface):
    
    @abc.abstractmethod
    def getExportOptionsView(self) -> Any:
        raise NotImplementedError
    
    @abc.abstractmethod
    def resetText(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def setText(self, text: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def appendText(self, text: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def disableView(self) -> None:
        raise NotImplementedError
        
    @abc.abstractmethod
    def enableView(self) -> None:
        raise NotImplementedError

    class Callback(ViewInterface.CallbackInterface):
        @abc.abstractmethod
        def onBtnRunScenarioClicked(self) -> Any:
            raise NotImplementedError

        @abc.abstractmethod
        def onBtnRunExportClicked(self) -> Any:
            raise NotImplementedError
