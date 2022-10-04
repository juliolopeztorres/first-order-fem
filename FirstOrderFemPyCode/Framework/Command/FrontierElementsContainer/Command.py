import os
from typing import Dict

import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.FrontierElementsContainer.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.FrontierElementsContainer.ViewProvider import ViewProvider
import FirstOrderFemPyCode.Framework.Command.FrontierElementGroup.Command as FrontierElementGroupCommand
from FirstOrderFemPyCode.Framework.Command.Interface import CommandInterface

if FreeCAD.GuiUp:
    from PySide import QtCore


def createGroup():
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "frontierElementsContainer")

    obj.Label = FreeCAD.Qt.translate("FrontierElementsContainer", "FRONTIER_ELEMENTS_CONTAINER_LABEL")

    DataContainer(obj)

    if FreeCAD.GuiUp:
        ViewProvider(obj.ViewObject)

    obj.addObject(FrontierElementGroupCommand.createGroup())

    return obj


class Command(CommandInterface):

    def GetResources(self) -> Dict[str, str]:
        return {
            'Pixmap': os.path.join(Util.getModulePath(), "assets", "icons", "frontier-elements-container.png"),
            'MenuText': QtCore.QT_TRANSLATE_NOOP("FrontierElementsContainer", "MENU_TEXT"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("FrontierElementsContainer", "TOOLTIP")
        }

    def IsActive(self) -> bool:
        return FreeCAD.ActiveDocument is not None

    def Activated(self) -> None:
        createGroup()
        FreeCAD.ActiveDocument.recompute()
