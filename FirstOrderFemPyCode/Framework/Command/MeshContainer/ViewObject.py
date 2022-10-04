from typing import Any
from FirstOrderFemPyCode.Framework.Command.MeshContainer.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.Interface import ViewObjectInterface


class ViewObject(ViewObjectInterface):
    class MeshContainerDataContainer(ViewObjectInterface.ObjectInterface):
        Proxy: DataContainer
        
        Group: Any

    Object: MeshContainerDataContainer
