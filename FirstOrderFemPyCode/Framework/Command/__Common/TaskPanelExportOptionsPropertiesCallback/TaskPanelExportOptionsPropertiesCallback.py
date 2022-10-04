from typing import Union
from FirstOrderFemPyCode.Framework.View.TaskPanelExportOptionsPropertiesViewInterface import MatPlotLibTypeViewLabel, RenderOptionViewLabel, TaskPanelExportOptionsPropertiesViewInterface

class TaskPanelExportOptionsPropertiesCallback(TaskPanelExportOptionsPropertiesViewInterface.Callback):
    _exportOptionsModel: TaskPanelExportOptionsPropertiesViewInterface.OptionsModel

    def onInputChanged(self, input: str, value: Union[RenderOptionViewLabel, MatPlotLibTypeViewLabel, int]) -> None:
        self._exportOptionsModel.__dict__[input] = value
