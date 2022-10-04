
from typing import Any

from FirstOrderFemPyCode.Framework.Command.Interface import DataContainerInterface
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.View.TaskPanelExportOptionsPropertiesViewInterface import RenderOptionViewLabel, MatPlotLibTypeViewLabel, TaskPanelExportOptionsPropertiesViewInterface

class DataContainer(DataContainerInterface):
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "ExportOptions"
        self.initProperties(obj)

    def initProperties(self, obj: Any) -> None:
        if Util.addObjectProperty(
            obj,
            'RenderOption',
            [renderOption.value for renderOption in RenderOptionViewLabel],
            "App::PropertyEnumeration",
            "Export options",
            "Output rendering option"
        ):
            obj.RenderOption = RenderOptionViewLabel.VTK.value

        if Util.addObjectProperty(
            obj,
            'MatPlotLibType',
            [matPlotLibType.value for matPlotLibType in MatPlotLibTypeViewLabel],
            "App::PropertyEnumeration",
            "Export options",
            "Output Matplotlib representation type"
        ):
            obj.MatPlotLibType = MatPlotLibTypeViewLabel.MIDDLE_POINTS.value

        Util.addObjectProperty(
            obj,
            'PointsPerDirection',
            25,
            "App::PropertyInteger",
            "Export options",
            "If plotting CARTESIAN type, how many points per direction to draw"
        )

    def onDocumentRestored(self, obj: Any) -> None:
        self.initProperties(obj)

    def execute(self, obj: Any) -> None:
        pass

    def updateModel(self, obj: Any, model: TaskPanelExportOptionsPropertiesViewInterface.OptionsModel) -> None:
        obj.RenderOption = model.renderOption.value
        obj.MatPlotLibType = model.matPlotLibType.value
        obj.PointsPerDirection = model.pointsPerDirection
