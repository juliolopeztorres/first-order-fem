from typing import Any
from FirstOrderFemPyCode.Framework.Command.FrontierElementGroup.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.Interface import ViewObjectInterface


class ViewObject(ViewObjectInterface):
    class FrontierElementGroupDataContainer(ViewObjectInterface.ObjectInterface):
        Proxy: DataContainer
        
        Group: Any

    Object: FrontierElementGroupDataContainer
