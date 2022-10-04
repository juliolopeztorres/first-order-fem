from typing import Any
from FirstOrderFemPyCode.Framework.Command.PrescribedNodeGroup.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.Interface import ViewObjectInterface


class ViewObject(ViewObjectInterface):
    class PrescribedNodeGroupDataContainer(ViewObjectInterface.ObjectInterface):
        Proxy: DataContainer
        
        Voltage: float
        Group: Any

    Object: PrescribedNodeGroupDataContainer
