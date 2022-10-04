from FirstOrderFemPyCode.Framework.Command.FrontierElementsContainer.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.Interface import ViewObjectInterface


class ViewObject(ViewObjectInterface):
    class FrontierElementsContainerDataContainer(ViewObjectInterface.ObjectInterface):
        Proxy: DataContainer

    Object: FrontierElementsContainerDataContainer
