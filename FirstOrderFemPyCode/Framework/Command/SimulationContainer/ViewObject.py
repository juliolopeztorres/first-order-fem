from typing import Any
from FirstOrderFemPyCode.Framework.Command.SimulationContainer.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.Interface import ViewObjectInterface


class ViewObject(ViewObjectInterface):
    class SimulationContainerDataContainer(ViewObjectInterface.ObjectInterface):
        Proxy: DataContainer
        
        Group: Any

    Object: SimulationContainerDataContainer
