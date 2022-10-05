from typing import Any, Dict, List, Optional

from FirstOrderFemPyCode.Data.DataRepository import DataRepository
from FirstOrderFemPyCode.Data.ExtractorService import ExtractorService
from FirstOrderFemPyCode.Data.VtkService import VtkService
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsRepositoryInterface import \
    ExtractSimulationResultsRepositoryInterface
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import \
    SimulationDescription


class ExtractSimulationResultsRepository(DataRepository, ExtractSimulationResultsRepositoryInterface):
    __simulationDescription: SimulationDescription
    __nodeVoltages: Dict[int, float]
    __extractorService: ExtractorService
    __vtkService: VtkService

    def setSimulationInformation(self: 'ExtractSimulationResultsRepository', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        self.__simulationDescription = simulationDescription
        self.__nodeVoltages = nodeVoltages if nodeVoltages else self._getNodeVoltages(simulationDescription.path, 'solution.json')
        
        self.__extractorService = ExtractorService(simulationDescription.mesh, self.__nodeVoltages)
        self.__vtkService = VtkService(self.__simulationDescription)

    def extractInfoForVtk(self: 'ExtractSimulationResultsRepository') -> List[Any]:
        return self.__extractorService.extractPlotInfo(ExtractorService.Plot.VTK)

    def extractInfoForPlotElementsCenter(self: 'ExtractSimulationResultsRepository') -> List[Any]:
        return self.__extractorService.extractPlotInfo(ExtractorService.Plot.ELEMENT_CENTER)
        
    def extractInfoForPlotCartesianGrid(self: 'ExtractSimulationResultsRepository') -> List[Any]:
        return self.__extractorService.extractPlotInfo(ExtractorService.Plot.CARTESIAN_GRID, self.__simulationDescription.exportOptions.pointsPerDirection)

    def extractChargeInfo(self: 'ExtractSimulationResultsRepository') -> Dict[str, List[Any]]:
        frontierInfo: Dict[str, List[Any]] = {}
        
        for frontierElementsGroupName, elements in self.__simulationDescription.frontierElementsGroups.items():
            frontierInfo[frontierElementsGroupName] = self.__extractorService.getFrontierElementsValues(frontierElementsGroupName, elements)
        
        return frontierInfo

    def saveInfoToFile(self: 'ExtractSimulationResultsRepository', info: List[Any]) -> None:
        self._writeJsonContent(self.__simulationDescription.path, 'plot-info.json', info)
    
    def saveChargeInfoToFile(self: 'ExtractSimulationResultsRepository', chargeInfo: Dict[str, List[Any]]) -> None:
        for offsetName, frontierElectricFieldVector in chargeInfo.items():
            self._writeJsonContent(self.__simulationDescription.path, f'relevant-electric-field-vector_{offsetName}.json', frontierElectricFieldVector)
    
    def exportToVtk(self: 'ExtractSimulationResultsRepository', info: List[Any]) -> None:
        self.__vtkService.export(self.__nodeVoltages, info)
