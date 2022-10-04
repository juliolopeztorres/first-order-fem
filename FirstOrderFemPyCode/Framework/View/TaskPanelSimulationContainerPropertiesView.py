from typing import Any, List, Optional
from FirstOrderFemPyCode.Framework.View.TaskPanelExportOptionsPropertiesViewInterface import TaskPanelExportOptionsPropertiesViewInterface
from FirstOrderFemPyCode.Framework.View.TaskPanelSimulationContainerPropertiesViewInterface import TaskPanelSimulationContainerPropertiesViewInterface
from FirstOrderFemPyCode.Framework.Service.UiLoaderServiceInterface import UiLoaderServiceInterface
from FirstOrderFemPyCode.Framework.Command.SimulationContainer.ViewObject import ViewObject


class TaskPanelSimulationContainerPropertiesView(TaskPanelSimulationContainerPropertiesViewInterface):
    __callback: TaskPanelSimulationContainerPropertiesViewInterface.Callback
    form: Any
    __exportOptionsView: Optional[TaskPanelExportOptionsPropertiesViewInterface] = None

    def __init__(
        self,
        uiLoaderService: UiLoaderServiceInterface,
        callback: TaskPanelSimulationContainerPropertiesViewInterface.Callback,
        obj: ViewObject.SimulationContainerDataContainer,
        childs: List[Any] = None
    ):
        self.form = uiLoaderService.load("TaskPanelSimulationContainerProperties")
        self.__callback = callback
        
        if childs:
            if len(childs) != 1:
                raise Exception(
                    'Solver Options view expect to have only one Mesher child'
                )

            # This strong reference is mandatory to keep events working
            self.__exportOptionsView: TaskPanelExportOptionsPropertiesViewInterface = childs[0]

            if self.__exportOptionsView:
                self.form.exportOptionsFrame.layout().addWidget(
                    self.__exportOptionsView.getActualView()
                )
        else:
            self.form.exportOptions.setText(self.form.exportOptions.text() + ': ~')
            
        self.form.btnRunScenario.clicked.connect(self.__onBtnRunScenarioClicked)
        self.form.btnRunExport.clicked.connect(self.__onBtnRunExportClicked)

    def __onBtnRunScenarioClicked(self: 'TaskPanelSimulationContainerPropertiesView') -> None:
        self.__callback.onBtnRunScenarioClicked()
        
    def __onBtnRunExportClicked(self: 'TaskPanelSimulationContainerPropertiesView') -> None:
        self.__callback.onBtnRunExportClicked()

    def accept(self: 'TaskPanelSimulationContainerPropertiesView') -> None:
        self.__callback.onAccept()

    def reject(self: 'TaskPanelSimulationContainerPropertiesView') -> None:
        self.__callback.onReject()

    def closing(self: 'TaskPanelSimulationContainerPropertiesView') -> None:
        self.__callback.onClose()

    def getExportOptionsView(self) -> Any:
        return self.__exportOptionsView
