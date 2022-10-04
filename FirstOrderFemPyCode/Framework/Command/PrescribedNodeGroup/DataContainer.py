
from typing import Any

from FirstOrderFemPyCode.Framework.Command.Interface import DataContainerInterface
import FirstOrderFemPyCode.Framework.Util as Util

class DataContainer(DataContainerInterface):
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "PrescribedNodeGroup"
        self.initProperties(obj)

    def initProperties(self, obj: Any) -> None:
        Util.addObjectProperty(
            obj,
            'Voltage',
            0.0,
            "App::PropertyFloat",
            "Prescribed Node Group Properties",
            "Voltage to be appled to the nodes"
        )

    def onDocumentRestored(self, obj: Any) -> None:
        self.initProperties(obj)

    def saveVoltage(self, obj: Any, voltage: float) -> None:
        obj.Voltage = voltage

    def execute(self, obj: Any) -> None:
        pass
