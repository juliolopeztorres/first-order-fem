import os
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsUseCase import ExtractSimulationResultsUseCase
import FreeCAD

from typing import Any, Dict, Optional, Union
from FirstOrderFemPyCode.Framework.View.TaskPanelExportOptionsPropertiesViewInterface import MatPlotLibTypeViewLabel, RenderOptionViewLabel, TaskPanelExportOptionsPropertiesViewInterface
from FirstOrderFemPyCode.Framework.View.TaskPanelSimulationContainerPropertiesViewInterface import TaskPanelSimulationContainerPropertiesViewInterface

import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.SimulationContainer.ViewObject import ViewObject
from FirstOrderFemPyCode.Framework.Command.Interface import ViewProviderInterface
from FirstOrderFemPyCode.Framework.Container import Container, Service, View
from FirstOrderFemPyCode.Framework.Command.ExportOptions.ViewObject import ViewObject as ExportOptionsViewObject
from FirstOrderFemPyCode.Framework.Command.__Common.TaskPanelExportOptionsPropertiesCallback.TaskPanelExportOptionsPropertiesCallback import TaskPanelExportOptionsPropertiesCallback
from FirstOrderFemPyCode.Framework.Mapper.SimulationDescriptionMapper import SimulationDescriptionMapper
from FirstOrderFemPyCode.Domain.RunSimulationUseCase.RunSimulationUseCase import RunSimulationUseCase
from FirstOrderFemPyCode.Framework.Container import Container
import FirstOrderFemPyCode.Framework.Util as Util
from pathlib import Path

if FreeCAD.GuiUp:
    import FreeCADGui

class ViewProvider(
    ViewProviderInterface, 
    TaskPanelSimulationContainerPropertiesViewInterface.Callback,
    TaskPanelExportOptionsPropertiesCallback
    ):
    __viewObject: ViewObject
    __view: Optional[TaskPanelSimulationContainerPropertiesViewInterface] = None
    __exportOptionsView: Optional[TaskPanelExportOptionsPropertiesViewInterface] = None
    
    __runSimulationUseCase: RunSimulationUseCase
    __extractSimulationResultsUseCase: ExtractSimulationResultsUseCase
    
    __exportOptionsDataObject: Optional[ExportOptionsViewObject.ExportOptionsDataContainer] = None
    
    __lastSolution: Optional[Dict[int, float]] = None

    def __init__(self, vobj: ViewObject):
        vobj.Proxy = self

    def __prepareExportOptionsView(self: 'ViewProvider') -> Any:
        if not self.__exportOptionsDataObject or not self.__view or not self.__exportOptionsView:
            return

        self.__exportOptionsView.loadData(self._exportOptionsModel)
    
    def __getExportOptionsModel(self: 'ViewProvider') -> Any:
        if not self.__exportOptionsDataObject:
            raise Exception('No export options data object present')
        
        dataContainer = self.__exportOptionsDataObject
        
        return TaskPanelExportOptionsPropertiesViewInterface.OptionsModel(
            RenderOptionViewLabel(dataContainer.RenderOption),
            MatPlotLibTypeViewLabel(dataContainer.MatPlotLibType),
            dataContainer.PointsPerDirection
        )

    def __saveExportOptionsModel(self) -> None:
        if not self.__exportOptionsDataObject:
            return

        self.__exportOptionsDataObject.Proxy.updateModel(
            self.__exportOptionsDataObject,
            self._exportOptionsModel
        )

    def __cleanAndCreateSimulationFolder(self, path: str) -> None:
        Util.removeFolder(path)
        Path(path).mkdir(exist_ok=True, parents=True)

    def getIcon(self) -> str:
        return os.path.join(Util.getModulePath(), "assets", "icons", "analysis.png")

    def attach(self, vobj: ViewObject) -> None:
        self.__viewObject = vobj
        self.__runSimulationUseCase = Container.getService(Service.RUN_SIMULATION_USE_CASE)
        self.__extractSimulationResultsUseCase = Container.getService(Service.EXTRACT_SIMULATION_RESULTS_USE_CASE)

    def doubleClicked(self, vobj: ViewObject) -> bool:
        doc = FreeCADGui.getDocument(vobj.Object.Document)

        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)

        return True

    def setEdit(self, viewObject: ViewObject, mode: int) -> bool:
        FreeCADGui.Selection.clearSelection()


        group = viewObject.Object.Group
        if len(group) > 0:
            from FirstOrderFemPyCode.Framework.Command.ExportOptions.ViewProvider import \
                ViewProvider as ExportOptionsViewProvider
            dataObjects = Util.getDataObjectsWithViewObjectProxyInstance(
                group,
                ExportOptionsViewProvider
            )
            if len(dataObjects) == 1:
                self.__exportOptionsDataObject = dataObjects[0]
                self._exportOptionsModel = self.__getExportOptionsModel()
        else:
            self.__exportOptionsDataObject = None

        self.__view: TaskPanelSimulationContainerPropertiesViewInterface = Container.getView(
            View.TASK_PANEL_SIMULATION_CONTAINER_PROPERTIES_VIEW,
            self,
            viewObject.Object,
            childs=[
                View.TASK_PANEL_EXPORT_OPTIONS_PROPERTIES_VIEW
            ] if self.__exportOptionsDataObject else None
        )

        if self.__view:            
            self.__exportOptionsView = self.__view.getExportOptionsView()
            self.__prepareExportOptionsView()
            
            FreeCADGui.Control.showDialog(self.__view)

        return True

    def unsetEdit(self, vobj: ViewObject, mode) -> None:
        FreeCADGui.Control.closeDialog()

    def onAccept(self) -> None:
        self.__saveExportOptionsModel()
        
        FreeCADGui.ActiveDocument.resetEdit()

    def onReject(self) -> None:
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()

    def onClose(self) -> None:
        pass

    def onBtnRunScenarioClicked(self) -> Any:
        simulationDescription = SimulationDescriptionMapper.map(
            self.__viewObject.Object, 
            Util.getSimulationOutputFolderPath(FreeCAD.ActiveDocument.FileName)
        )
        
        self.__cleanAndCreateSimulationFolder(simulationDescription.path)
        self.__lastSolution = self.__runSimulationUseCase.run(simulationDescription)
        
        Util.openFileManager(simulationDescription.path)

    def onBtnRunExportClicked(self) -> Any:
        self.__extractSimulationResultsUseCase.extract(
            SimulationDescriptionMapper.map(
                self.__viewObject.Object, 
                Util.getSimulationOutputFolderPath(FreeCAD.ActiveDocument.FileName)
            ), 
            self.__lastSolution
        )

    def onInputChanged(self, input: str, value: Union[RenderOptionViewLabel, MatPlotLibTypeViewLabel, int]) -> None:
        TaskPanelExportOptionsPropertiesCallback.onInputChanged(self, input, value)
        self.__saveExportOptionsModel()
