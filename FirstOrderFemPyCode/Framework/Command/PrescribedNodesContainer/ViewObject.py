from FirstOrderFemPyCode.Framework.Command.PrescribedNodesContainer.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.Interface import ViewObjectInterface


class ViewObject(ViewObjectInterface):
    class PrescribedNodesContainerDataContainer(ViewObjectInterface.ObjectInterface):
        Proxy: DataContainer

    Object: PrescribedNodesContainerDataContainer
