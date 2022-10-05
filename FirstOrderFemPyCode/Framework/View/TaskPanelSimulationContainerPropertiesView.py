from typing import Any, List, Optional
from PySide import QtGui

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

        self.form.textReport.verticalScrollBar().rangeChanged.connect(self.__resizeScroll)

    def __resizeScroll(self, min, maxi):
        self.form.textReport.verticalScrollBar().setValue(maxi)

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

    def setText(self, text: str) -> None:
        self.form.textReport.setPlainText(text)
        self.form.textReport.moveCursor(QtGui.QTextCursor.End)

    def appendText(self, text: str) -> None:
        self.form.textReport.insertPlainText(text)

    def resetText(self) -> None:
        self.form.textReport.clear()
