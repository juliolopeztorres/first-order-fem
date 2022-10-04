import abc
from typing import Any
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface

class TaskPanelSimulationContainerPropertiesViewInterface(ViewInterface):
    
    @abc.abstractmethod
    def getExportOptionsView(self) -> Any:
        raise NotImplementedError
    
    class Callback(ViewInterface.CallbackInterface):
        @abc.abstractmethod
        def onBtnRunScenarioClicked(self) -> Any:
            raise NotImplementedError

        @abc.abstractmethod
        def onBtnRunExportClicked(self) -> Any:
            raise NotImplementedError
