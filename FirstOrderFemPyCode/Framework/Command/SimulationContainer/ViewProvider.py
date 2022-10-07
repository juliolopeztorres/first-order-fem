import os
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsUseCase import ExtractSimulationResultsUseCase
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription
from FirstOrderFemPyCode.Framework.Command.SimulationContainer.Thread import Thread, ThreadOutput
from FirstOrderFemPyCode.Framework.View.ProgressBarViewInterface import ProgressBarViewInterface
import FreeCAD

if FreeCAD.GuiUp:
    import FreeCADGui

from typing import Any, Dict, List, Optional, Union
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

class ViewProvider(
    ViewProviderInterface, 
    TaskPanelSimulationContainerPropertiesViewInterface.Callback,
    TaskPanelExportOptionsPropertiesCallback,
    ProgressBarViewInterface.CallbackInterface
    ):
    __viewObject: ViewObject
    __view: Optional[TaskPanelSimulationContainerPropertiesViewInterface] = None
    __exportOptionsView: Optional[TaskPanelExportOptionsPropertiesViewInterface] = None
    
    __runSimulationUseCase: RunSimulationUseCase
    __extractSimulationResultsUseCase: ExtractSimulationResultsUseCase
    
    __exportOptionsDataObject: Optional[ExportOptionsViewObject.ExportOptionsDataContainer] = None
    
    __lastSolution: Optional[Dict[int, float]] = None

    __progressBar: Optional[ProgressBarViewInterface] = None
    thread: Thread = Thread()

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

    def __showChargeInfo(self, chargeInfo: Dict[str, List[Any]]) -> None:
        chargeOnFrontierText = FreeCAD.Qt.translate("SimulationContainer", "CHARGE_ON_FRONTIER_OUTPUT")
        
        if not self.__view:
            return
        
        chargeInfoParsed: List[str] = []
        for frontierElementsGroupName, frontierElectricFieldVector in chargeInfo.items():
            totalCharge = sum([values['charge'] for values in frontierElectricFieldVector])

            chargeInfoParsed.append(f'{chargeOnFrontierText} {frontierElementsGroupName}: {totalCharge}C\n\n')

        self.__view.appendText(''.join(chargeInfoParsed))

    def getIcon(self) -> str:
        return os.path.join(Util.getModulePath(), "assets", "icons", "analysis.png")

    def attach(self, vobj: ViewObject) -> None:
        self.__viewObject = vobj
        self.__runSimulationUseCase = Container.getService(Service.RUN_SIMULATION_USE_CASE)
        self.__extractSimulationResultsUseCase = Container.getService(Service.EXTRACT_SIMULATION_RESULTS_USE_CASE)

        self.thread.signals.error.connect(self.threadError)
        self.thread.signals.finished.connect(self.threadFinished)
        self.thread.signals.status.connect(self.threadStatus)
        self.thread.signals.update.connect(self.updateProgress)

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
        self.__progressBar: ProgressBarViewInterface = Container.getView(
            View.PROGRESS_BAR_VIEW, 
            self
        )
        
        if self.__progressBar:
            self.__progressBar.show()
            
            
        self.thread.runSimulationUseCase = self.__runSimulationUseCase
        self.thread.object = self.__viewObject.Object
        self.thread.start()
        
        # TODO: Disable UI

    def onBtnRunExportClicked(self) -> Any:
        if not self.__view:
            return

        chargeInfo = self.__extractSimulationResultsUseCase.extract(
            SimulationDescriptionMapper.map(
                self.__viewObject.Object, 
                Util.getSimulationOutputFolderPath(FreeCAD.ActiveDocument.FileName)
            ), 
            self.__lastSolution
        )

        self.__view.resetText()
        self.__showChargeInfo(chargeInfo)

    def onInputChanged(self, input: str, value: Union[RenderOptionViewLabel, MatPlotLibTypeViewLabel, int]) -> None:
        TaskPanelExportOptionsPropertiesCallback.onInputChanged(self, input, value)
        self.__saveExportOptionsModel()

    def threadStatus(self, msg) -> None:
        print(msg)
        if self.__progressBar:
            self.__progressBar.showText(msg)

    def threadError(self, msg) -> None:
        print(msg)
        if self.__progressBar:
            self.__progressBar.showText(msg)
            
        # TODO: Enable UI

    def threadFinished(self, status: bool, threadOutput: ThreadOutput) -> None:
        self.thread.terminate()
          
        # TODO: Enable UI
        
        if not status:
            if self.__progressBar:
                self.__progressBar.resetText()
                self.__progressBar.closing()
                self.__progressBar = None

            return

        self.threadStatus('Opening simulation output folder...')
        self.updateProgress(50)

        simulationOutput = threadOutput.simulationOutput
        simulationDescription: SimulationDescription = simulationOutput['simulationDescription']
    
        self.__lastSolution = simulationOutput['nodeVoltages']
        
        Util.openFileManager(simulationDescription.path)

        if not self.__view:
            return
        
        self.__view.resetText()
        energyText = FreeCAD.Qt.translate("SimulationContainer", "ENERGY_OUTPUT")
        self.__view.setText(f'{energyText}:{simulationOutput["energy"]}J\n\n')

        self.threadStatus('Extracting relevant output info...')
        self.updateProgress(60)

        chargeInfo = self.__extractSimulationResultsUseCase.extract(simulationDescription, self.__lastSolution)

        self.__showChargeInfo(chargeInfo)
        
        if self.__progressBar:
            self.__progressBar.resetText()
            self.__progressBar.closing()
            self.__progressBar = None

    def updateProgress(self, progress: int) -> None:
        if self.__progressBar:
            self.__progressBar.setProgress(progress)
