
from typing import Any

from FirstOrderFemPyCode.Framework.Command.Interface import DataContainerInterface

class DataContainer(DataContainerInterface):
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "FrontierElementsContainer"
        self.initProperties(obj)

    def initProperties(self, obj: Any) -> None:
        pass

    def onDocumentRestored(self, obj: Any) -> None:
        self.initProperties(obj)

    def execute(self, obj: Any) -> None:
        pass
