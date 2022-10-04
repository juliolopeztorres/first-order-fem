from enum import Enum, unique

@unique
class RenderOption(Enum):
    VTK = 'VTK'
    MATPLOTLIB = 'MATPLOTLIB'
    
@unique
class MatPlotLibType(Enum):
    CARTESIAN = 'CARTESIAN'
    MIDDLE_POINTS = 'MIDDLE_POINTS'

class ExportOptions:
    renderOption: RenderOption
    matPlotLibType: MatPlotLibType
    pointsPerDirection: int

    def __init__(
        self, 
        renderOption: RenderOption,
        matPlotLibType: MatPlotLibType,
        pointsPerDirection,
    ) -> None:
        self.renderOption = renderOption
        self.matPlotLibType = matPlotLibType
        self.pointsPerDirection = pointsPerDirection
