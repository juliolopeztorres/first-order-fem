from typing import Any, List
from FirstOrderFemPyCode.Framework.View.TaskPanelPrescribedNodeGroupPropertiesViewInterface import TaskPanelPrescribedNodeGroupPropertiesViewInterface
from FirstOrderFemPyCode.Framework.Service.UiLoaderServiceInterface import UiLoaderServiceInterface
from FirstOrderFemPyCode.Framework.Command.PrescribedNodeGroup.ViewObject import ViewObject
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface

class TaskPanelPrescribedNodeGroupPropertiesView(TaskPanelPrescribedNodeGroupPropertiesViewInterface):
    __callback: TaskPanelPrescribedNodeGroupPropertiesViewInterface.Callback
    form: Any

    def __init__(
        self,
        uiLoaderService: UiLoaderServiceInterface,
        callback: TaskPanelPrescribedNodeGroupPropertiesViewInterface.Callback,
        obj: ViewObject.PrescribedNodeGroupDataContainer,
        childs: List[ViewInterface] = None
    ):
        self.form = uiLoaderService.load("TaskPanelPrescribedNodeGroupProperties")
        self.__callback = callback

    def loadVoltage(self, voltage: float) -> None:
        self.form.inputVoltage.setText("{:.2f}".format(voltage))

    def accept(self) -> None:
        try:
            self.__callback.onVoltageChanged(
                float(self.form.inputVoltage.text())
            )
        except:
            self.__callback.onReject()

    def reject(self) -> None:
        self.__callback.onReject()

    def closing(self) -> None:
        self.__callback.onClose()
