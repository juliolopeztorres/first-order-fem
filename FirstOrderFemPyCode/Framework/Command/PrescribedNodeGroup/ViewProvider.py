import os
from typing import Optional

import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.PrescribedNodeGroup.ViewObject import ViewObject
from FirstOrderFemPyCode.Framework.Command.Interface import ViewProviderInterface
from FirstOrderFemPyCode.Framework.Container import Container, View
from FirstOrderFemPyCode.Framework.View.TaskPanelPrescribedNodeGroupPropertiesViewInterface import TaskPanelPrescribedNodeGroupPropertiesViewInterface

if FreeCAD.GuiUp:
    import FreeCADGui


class ViewProvider(ViewProviderInterface, TaskPanelPrescribedNodeGroupPropertiesViewInterface.Callback):
    __viewObject: ViewObject
    __view: Optional[TaskPanelPrescribedNodeGroupPropertiesViewInterface] = None

    def __init__(self, vobj: ViewObject):
        vobj.Proxy = self

    def getIcon(self) -> str:
        return os.path.join(Util.getModulePath(), "assets", "icons", "scenario.png")

    def attach(self, vobj: ViewObject) -> None:
        self.__viewObject = vobj

    def doubleClicked(self, vobj: ViewObject) -> bool:
        doc = FreeCADGui.getDocument(vobj.Object.Document)

        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)

        return True

    def setEdit(self, vobj: ViewObject, mode) -> bool:
        FreeCADGui.Selection.clearSelection()

        self.__view: TaskPanelPrescribedNodeGroupPropertiesViewInterface = Container.getView(
            View.TASK_PANEL_PRESCRIBED_NODE_GROUP_PROPERTIES_VIEW,
            self,
            vobj.Object
        )

        if self.__view:
            self.__view.loadVoltage(vobj.Object.Voltage)
            FreeCADGui.Control.showDialog(self.__view)

        return True

    def unsetEdit(self, vobj: ViewObject, mode) -> None:
        FreeCADGui.Control.closeDialog()

    def onAccept(self) -> None:
        FreeCADGui.ActiveDocument.resetEdit()

    def onReject(self) -> None:
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()

    def onClose(self) -> None:
        pass

    def onVoltageChanged(self, voltage: float) -> None:
        self.__viewObject.Object.Proxy.saveVoltage(
            self.__viewObject.Object,
            voltage
        )
        
        self.onAccept()
