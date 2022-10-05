from typing import Any, Dict, List, Optional

from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsRepositoryInterface import \
    ExtractSimulationResultsRepositoryInterface
from FirstOrderFemPyCode.Domain.Model.ExportOptions import (MatPlotLibType,
                                                            RenderOption)
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import \
    SimulationDescription
from FirstOrderFemPyCode.Domain.PlotResultsUseCase.PlotResultsUseCase import \
    PlotResultsUseCase


class ExtractSimulationResultsUseCase:
    __repository: ExtractSimulationResultsRepositoryInterface

    def __init__(self, repository: ExtractSimulationResultsRepositoryInterface) -> None:
        self.__repository = repository

    def extract(self: 'ExtractSimulationResultsUseCase', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> Dict[str, List[Any]]:
        # Init simulation info
        self.__repository.setSimulationInformation(
            simulationDescription, nodeVoltages)

        # Extract relevant information from the elements
        if simulationDescription.exportOptions.renderOption == RenderOption.VTK:
            info = self.__repository.extractInfoForVtk()
        elif simulationDescription.exportOptions.matPlotLibType == MatPlotLibType.MIDDLE_POINTS:
            info = self.__repository.extractInfoForPlotElementsCenter()
        else:
            info = self.__repository.extractInfoForPlotCartesianGrid()

        # Save that information to file (later to consult)
        self.__repository.saveInfoToFile(info)

        # Show results to the user
        if simulationDescription.exportOptions.renderOption == RenderOption.VTK:
            self.__repository.exportToVtk(info)
        else:
            PlotResultsUseCase().plot(info)

        chargeInfo = self.__repository.extractChargeInfo()
        self.__repository.saveChargeInfoToFile(chargeInfo)
        
        return chargeInfo
