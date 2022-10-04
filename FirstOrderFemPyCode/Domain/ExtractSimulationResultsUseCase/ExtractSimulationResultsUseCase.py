from typing import Dict, Optional
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsRepositoryInterface import ExtractSimulationResultsRepositoryInterface
from FirstOrderFemPyCode.Domain.Model.ExportOptions import MatPlotLibType, RenderOption
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription

class ExtractSimulationResultsUseCase:
    __repository: ExtractSimulationResultsRepositoryInterface
    
    def __init__(self, repository: ExtractSimulationResultsRepositoryInterface) -> None:
        self.__repository = repository

    def extract(self: 'ExtractSimulationResultsUseCase', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        self.__repository.setSimulationInformation(simulationDescription, nodeVoltages)
    
        if simulationDescription.exportOptions.renderOption == RenderOption.VTK:
            self.__repository.extractInfoForVtk()
        elif simulationDescription.exportOptions.matPlotLibType == MatPlotLibType.MIDDLE_POINTS:
            self.__repository.extractInfoForPlotElementsCenter()
        else:
            self.__repository.extractInfoForPlotCartesianGrid()
            
        self.__repository.extractChargeInfo()
