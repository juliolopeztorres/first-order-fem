import abc
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface

class TaskPanelPrescribedNodeGroupPropertiesViewInterface(ViewInterface):
    
    @abc.abstractmethod
    def loadVoltage(self, voltage: float) -> None:
        raise NotImplementedError
    
    class Callback(ViewInterface.CallbackInterface):
        @abc.abstractmethod
        def onVoltageChanged(self, voltage: float) -> None:
            raise NotImplementedError
