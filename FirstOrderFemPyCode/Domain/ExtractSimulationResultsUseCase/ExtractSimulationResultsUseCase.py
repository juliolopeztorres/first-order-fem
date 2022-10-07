from typing import Any, Dict, Optional

from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsRepositoryInterface import \
    ExtractSimulationResultsRepositoryInterface
from FirstOrderFemPyCode.Domain.Model.ExportOptions import (MatPlotLibType,
                                                            RenderOption)
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import \
    SimulationDescription


class ExtractSimulationResultsUseCase:
    __repository: ExtractSimulationResultsRepositoryInterface

    def __init__(self, repository: ExtractSimulationResultsRepositoryInterface) -> None:
        self.__repository = repository

    def extract(self: 'ExtractSimulationResultsUseCase', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> Dict[str, Any]:
        # Init simulation info
        self.__repository.setSimulationInformation(
            simulationDescription, nodeVoltages)

        # Extract relevant information from the elements
        if simulationDescription.exportOptions.renderOption == RenderOption.VTK:
            plotInfo = self.__repository.extractInfoForVtk()
        elif simulationDescription.exportOptions.matPlotLibType == MatPlotLibType.MIDDLE_POINTS:
            plotInfo = self.__repository.extractInfoForPlotElementsCenter()
        else:
            plotInfo = self.__repository.extractInfoForPlotCartesianGrid()

        # Save that information to file (later to consult)
        self.__repository.saveInfoToFile(plotInfo)

        chargeInfo = self.__repository.extractChargeInfo()
        self.__repository.saveChargeInfoToFile(chargeInfo)
        
        return {
            'plotInfo': plotInfo,
            'chargeInfo': chargeInfo
        }
