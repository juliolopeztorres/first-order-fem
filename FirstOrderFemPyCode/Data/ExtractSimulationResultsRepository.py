from typing import Dict, Optional
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsRepositoryInterface import ExtractSimulationResultsRepositoryInterface
from FirstOrderFemPyCode.Domain.Model.ExportVtk import ExportVtk
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription
from FirstOrderFemPyCode.Domain.Model.Extractor import Extractor
from FirstOrderFemPyCode.Domain.Model.Plot import Plot

class ExtractSimulationResultsRepository(ExtractSimulationResultsRepositoryInterface):
    __simulationDescription: SimulationDescription
    __nodeVoltages: Optional[Dict[int, float]]
    __extractor: Extractor

    def setSimulationInformation(self: 'ExtractSimulationResultsRepository', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        self.__simulationDescription = simulationDescription
        self.__nodeVoltages = nodeVoltages
        
        self.__extractor = Extractor(simulationDescription.path, simulationDescription.mesh, nodeVoltages)

    def extractInfoForVtk(self: 'ExtractSimulationResultsRepository') -> None:
        EVectorInfo = self.__extractor.extractPlotInfo(Extractor.Plot.VTK)
        
        ExportVtk(self.__simulationDescription.path).run(self.__simulationDescription.mesh, self.__nodeVoltages, EVectorInfo)

    def extractInfoForPlotElementsCenter(self: 'ExtractSimulationResultsRepository') -> None:
        self.__extractor.extractPlotInfo(Extractor.Plot.ELEMENT_CENTER)
        
        Plot(self.__simulationDescription.path).run()

    def extractInfoForPlotCartesianGrid(self: 'ExtractSimulationResultsRepository') -> None:
        self.__extractor.extractPlotInfo(Extractor.Plot.CARTESIAN_GRID, self.__simulationDescription.exportOptions.pointsPerDirection)
        
        Plot(self.__simulationDescription.path).run()

    def extractChargeInfo(self: 'ExtractSimulationResultsRepository') -> None:
        for frontierElementsGroupName, elements in self.__simulationDescription.frontierElementsGroups.items():
            print(f'Total charge on frontier {frontierElementsGroupName}: {self.__extractor.extractChargeOnFrontier(frontierElementsGroupName, elements)}C\n')
