import os
from typing import Optional, Union
from FirstOrderFemPyCode.Framework.Command.__Common.TaskPanelExportOptionsPropertiesCallback.TaskPanelExportOptionsPropertiesCallback import TaskPanelExportOptionsPropertiesCallback
from FirstOrderFemPyCode.Framework.View.TaskPanelExportOptionsPropertiesViewInterface import MatPlotLibTypeViewLabel, RenderOptionViewLabel, TaskPanelExportOptionsPropertiesViewInterface

import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.ExportOptions.ViewObject import ViewObject
from FirstOrderFemPyCode.Framework.Command.Interface import ViewProviderInterface
from FirstOrderFemPyCode.Framework.Container import Container, View


if FreeCAD.GuiUp:
    import FreeCADGui

class ViewProvider(ViewProviderInterface, TaskPanelExportOptionsPropertiesCallback):
    __viewObject: ViewObject
    __view: Optional[TaskPanelExportOptionsPropertiesViewInterface] = None

    def __init__(self, vobj: ViewObject):
        vobj.Proxy = self

    def __getOptionsModel(self: 'ViewProvider') -> TaskPanelExportOptionsPropertiesViewInterface.OptionsModel:
        dataContainer = self.__viewObject.Object
        
        return TaskPanelExportOptionsPropertiesViewInterface.OptionsModel(
            RenderOptionViewLabel(dataContainer.RenderOption),
            MatPlotLibTypeViewLabel(dataContainer.MatPlotLibType),
            dataContainer.PointsPerDirection
        )

    def __saveModel(self) -> None:
        self.__viewObject.Object.Proxy.updateModel(
            self.__viewObject.Object,
            self._exportOptionsModel
        )

    def getIcon(self) -> str:
        return os.path.join(Util.getModulePath(), "assets", "icons", "export-options.png")

    def attach(self, vobj: ViewObject) -> None:
        self.__viewObject = vobj

    def doubleClicked(self, vobj: ViewObject) -> bool:
        doc = FreeCADGui.getDocument(vobj.Object.Document)

        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)

        return True

    def setEdit(self, vobj: ViewObject, mode) -> bool:
        FreeCADGui.Selection.clearSelection()

        self.__view: TaskPanelExportOptionsPropertiesViewInterface = Container.getView(
            View.TASK_PANEL_EXPORT_OPTIONS_PROPERTIES_VIEW,
            self,
            vobj.Object
        )

        self._exportOptionsModel = self.__getOptionsModel()

        if self.__view:
            self.__view.loadData(self._exportOptionsModel)
            FreeCADGui.Control.showDialog(self.__view)

        return True

    def unsetEdit(self, vobj: ViewObject, mode) -> None:
        FreeCADGui.Control.closeDialog()

    def onAccept(self) -> None:
        self.__saveModel()
        
        FreeCADGui.ActiveDocument.resetEdit()

    def onReject(self) -> None:
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()

    def onClose(self) -> None:
        pass
