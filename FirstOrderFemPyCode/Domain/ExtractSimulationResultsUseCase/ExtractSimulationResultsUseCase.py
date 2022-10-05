from typing import Dict, Optional
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsRepositoryInterface import ExtractSimulationResultsRepositoryInterface
from FirstOrderFemPyCode.Domain.Model.ExportOptions import MatPlotLibType, RenderOption
from FirstOrderFemPyCode.Domain.Model.Plot import Plot
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription

class ExtractSimulationResultsUseCase:
    __repository: ExtractSimulationResultsRepositoryInterface
    
    def __init__(self, repository: ExtractSimulationResultsRepositoryInterface) -> None:
        self.__repository = repository

    def extract(self: 'ExtractSimulationResultsUseCase', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        self.__repository.setSimulationInformation(simulationDescription, nodeVoltages)
    
        if simulationDescription.exportOptions.renderOption == RenderOption.VTK:
            info = self.__repository.extractInfoForVtk()
        elif simulationDescription.exportOptions.matPlotLibType == MatPlotLibType.MIDDLE_POINTS:
            info = self.__repository.extractInfoForPlotElementsCenter()
        else:
            info = self.__repository.extractInfoForPlotCartesianGrid()
            
        self.__repository.saveInfoToFile(info)
        
        if simulationDescription.exportOptions.renderOption == RenderOption.MATPLOTLIB:
            Plot().run(info)
            
        chargeInfo = self.__repository.extractChargeInfo()
        
        for frontierElementsGroupName, frontierElectricFieldVector in chargeInfo.items():
            totalCharge = sum([values['charge'] for values in frontierElectricFieldVector])
            print(f'Total charge on frontier {frontierElementsGroupName}: {totalCharge}C\n')
        
        self.__repository.saveChargeInfoToFile(chargeInfo)
