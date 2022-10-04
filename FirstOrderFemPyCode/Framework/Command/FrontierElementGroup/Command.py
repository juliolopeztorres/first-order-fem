import os
from typing import Dict

import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.FrontierElementGroup.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.FrontierElementGroup.ViewProvider import ViewProvider
from FirstOrderFemPyCode.Framework.Command.Interface import CommandInterface

if FreeCAD.GuiUp:
    from PySide import QtCore


def createGroup():
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "frontierElementGroup")

    obj.Label = FreeCAD.Qt.translate("FrontierElementGroup", "FRONTIER_ELEMENT_GROUP_LABEL")

    DataContainer(obj)

    if FreeCAD.GuiUp:
        ViewProvider(obj.ViewObject)

    return obj


class Command(CommandInterface):

    def GetResources(self) -> Dict[str, str]:
        return {
            'Pixmap': os.path.join(Util.getModulePath(), "assets", "icons", "nodes-elements-group.png"),
            'MenuText': QtCore.QT_TRANSLATE_NOOP("FrontierElementGroup", "MENU_TEXT"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("FrontierElementGroup", "TOOLTIP")
        }

    def IsActive(self) -> bool:
        return FreeCAD.ActiveDocument is not None

    def Activated(self) -> None:
        createGroup()
        FreeCAD.ActiveDocument.recompute()
