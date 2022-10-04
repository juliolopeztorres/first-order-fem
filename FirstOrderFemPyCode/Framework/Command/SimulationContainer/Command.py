import os
from typing import Dict

import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.SimulationContainer.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.SimulationContainer.ViewProvider import ViewProvider
from FirstOrderFemPyCode.Framework.Command.Interface import CommandInterface

import FirstOrderFemPyCode.Framework.Command.MeshContainer.Command as MeshContainer
import FirstOrderFemPyCode.Framework.Command.PrescribedNodesContainer.Command as PrescribedNodesContainer
import FirstOrderFemPyCode.Framework.Command.FrontierElementsContainer.Command as FrontierElementsContainer
import FirstOrderFemPyCode.Framework.Command.ExportOptions.Command as ExportOptions

if FreeCAD.GuiUp:
    from PySide import QtCore


def createGroup():
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "simulationContainer")

    obj.Label = FreeCAD.Qt.translate("SimulationContainer", "SIMULATION_CONTAINER_LABEL")

    DataContainer(obj)

    if FreeCAD.GuiUp:
        ViewProvider(obj.ViewObject)

    obj.addObject(MeshContainer.createGroup())
    obj.addObject(PrescribedNodesContainer.createGroup())
    obj.addObject(FrontierElementsContainer.createGroup())
    obj.addObject(ExportOptions.createGroup())

    return obj


class Command(CommandInterface):

    def GetResources(self) -> Dict[str, str]:
        return {
            'Pixmap': os.path.join(Util.getModulePath(), "assets", "icons", "analysis.png"),
            'MenuText': QtCore.QT_TRANSLATE_NOOP("SimulationContainer", "MENU_TEXT"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("SimulationContainer", "TOOLTIP")
        }

    def IsActive(self) -> bool:
        return FreeCAD.ActiveDocument is not None

    def Activated(self) -> None:
        createGroup()
        FreeCAD.ActiveDocument.recompute()
