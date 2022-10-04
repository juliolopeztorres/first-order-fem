
from typing import Any
from FirstOrderFemPyCode.Domain.Model.ExportOptions import ExportOptions as ModelExportOptions
from FirstOrderFemPyCode.Framework.Command.ExportOptions.ViewObject import ViewObject
from FirstOrderFemPyCode.Framework.View.TaskPanelExportOptionsPropertiesViewInterface import RenderOptionViewLabel, MatPlotLibTypeViewLabel

class ExportOptionsMapper:
    @staticmethod
    def map(exportOptionsFreeCAD: ViewObject.ExportOptionsDataContainer):        
        return ModelExportOptions(
            RenderOptionViewLabel(exportOptionsFreeCAD.RenderOption).getDomainRepresentation(),
            MatPlotLibTypeViewLabel(exportOptionsFreeCAD.MatPlotLibType).getDomainRepresentation(),
            exportOptionsFreeCAD.PointsPerDirection
        )
