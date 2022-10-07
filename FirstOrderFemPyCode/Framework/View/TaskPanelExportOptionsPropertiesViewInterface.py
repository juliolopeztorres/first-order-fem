import abc
from enum import Enum, unique
from typing import Any, Union
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface
from FirstOrderFemPyCode.Domain.Model.ExportOptions import RenderOption, MatPlotLibType

@unique
class RenderOptionViewLabel(Enum):
    VTK = 'VTK'
    MATPLOTLIB = 'MatPlot lib.'
    
    def getDomainRepresentation(self) -> RenderOption:
        return RenderOption(self.name)
    
@unique
class MatPlotLibTypeViewLabel(Enum):
    CARTESIAN = 'Cartesian'
    MIDDLE_POINTS = 'Middle points'
    
    def getDomainRepresentation(self) -> MatPlotLibType:
        return MatPlotLibType(self.name)

class TaskPanelExportOptionsPropertiesViewInterface:
    class OptionsModel:
        renderOption: RenderOptionViewLabel
        matPlotLibType: MatPlotLibTypeViewLabel
        pointsPerDirection: int

        def __init__(
            self, 
            renderOption: RenderOptionViewLabel,
            matPlotLibType: MatPlotLibTypeViewLabel,
            pointsPerDirection,
        ) -> None:
            self.renderOption = renderOption
            self.matPlotLibType = matPlotLibType
            self.pointsPerDirection = pointsPerDirection

    @abc.abstractmethod
    def loadData(self: 'TaskPanelExportOptionsPropertiesViewInterface', optionsModel: OptionsModel) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def getActualView(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def disableView(self) -> None:
        raise NotImplementedError
        
    @abc.abstractmethod
    def enableView(self) -> None:
        raise NotImplementedError

    class Callback(ViewInterface.CallbackInterface):
        @abc.abstractmethod
        def onInputChanged(self, input: str, value: Union[RenderOptionViewLabel, MatPlotLibTypeViewLabel, int]) -> None:
            raise NotImplementedError
