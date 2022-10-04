import os
from typing import Dict

import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.PrescribedNodesContainer.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.PrescribedNodesContainer.ViewProvider import ViewProvider
import FirstOrderFemPyCode.Framework.Command.PrescribedNodeGroup.Command as PrescribedNodeGroup
from FirstOrderFemPyCode.Framework.Command.Interface import CommandInterface

if FreeCAD.GuiUp:
    from PySide import QtCore


def createGroup():
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "prescribedNodesContainer")

    obj.Label = FreeCAD.Qt.translate("PrescribedNodesContainer", "PRESCRIBED_NODES_CONTAINER_LABEL")

    DataContainer(obj)

    if FreeCAD.GuiUp:
        ViewProvider(obj.ViewObject)

    obj.addObject(PrescribedNodeGroup.createGroup())

    return obj


class Command(CommandInterface):

    def GetResources(self) -> Dict[str, str]:
        return {
            'Pixmap': os.path.join(Util.getModulePath(), "assets", "icons", "prescribed-nodes-container.png"),
            'MenuText': QtCore.QT_TRANSLATE_NOOP("PrescribedNodesContainer", "MENU_TEXT"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("PrescribedNodesContainer", "TOOLTIP")
        }

    def IsActive(self) -> bool:
        return FreeCAD.ActiveDocument is not None

    def Activated(self) -> None:
        createGroup()
        FreeCAD.ActiveDocument.recompute()
