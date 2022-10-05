from typing import Any, Dict, List, Optional
from FirstOrderFemPyCode.Data.DataRepository import DataRepository
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsRepositoryInterface import ExtractSimulationResultsRepositoryInterface
from FirstOrderFemPyCode.Domain.Model.ExportVtk import ExportVtk
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription
from FirstOrderFemPyCode.Data.ExtractorService import ExtractorService
from FirstOrderFemPyCode.Domain.Model.Plot import Plot

class ExtractSimulationResultsRepository(DataRepository, ExtractSimulationResultsRepositoryInterface):
    __simulationDescription: SimulationDescription
    __nodeVoltages: Optional[Dict[int, float]]
    __extractor: ExtractorService

    def setSimulationInformation(self: 'ExtractSimulationResultsRepository', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        self.__simulationDescription = simulationDescription
        self.__nodeVoltages = nodeVoltages
        
        self.__extractor = ExtractorService(
            simulationDescription.mesh, 
            nodeVoltages if nodeVoltages else self._getNodeVoltages(simulationDescription.path, 'solution.json')
        )

    def extractInfoForVtk(self: 'ExtractSimulationResultsRepository') -> List[Any]:
        EVectorInfo = self.__extractor.extractPlotInfo(ExtractorService.Plot.VTK)
        
        ExportVtk(self.__simulationDescription.path).run(self.__simulationDescription.mesh, self.__nodeVoltages, EVectorInfo)
        
        return EVectorInfo

    def extractInfoForPlotElementsCenter(self: 'ExtractSimulationResultsRepository') -> List[Any]:
        return self.__extractor.extractPlotInfo(ExtractorService.Plot.ELEMENT_CENTER)
        
    def extractInfoForPlotCartesianGrid(self: 'ExtractSimulationResultsRepository') -> List[Any]:
        return self.__extractor.extractPlotInfo(ExtractorService.Plot.CARTESIAN_GRID, self.__simulationDescription.exportOptions.pointsPerDirection)

    def extractChargeInfo(self: 'ExtractSimulationResultsRepository') -> Dict[str, List[Any]]:
        frontierInfo: Dict[str, List[Any]] = {}
        
        for frontierElementsGroupName, elements in self.__simulationDescription.frontierElementsGroups.items():
            frontierInfo[frontierElementsGroupName] = self.__extractor.getFrontierElementsValues(frontierElementsGroupName, elements)
        
        return frontierInfo

    def saveInfoToFile(self: 'ExtractSimulationResultsRepository', info: List[Any]) -> None:
        self._writeJsonContent(self.__simulationDescription.path, 'plot-info.json', info)
    
    def saveChargeInfoToFile(self: 'ExtractSimulationResultsRepository', chargeInfo: Dict[str, List[Any]]) -> None:
        for offsetName, frontierElectricFieldVector in chargeInfo.items():
            self._writeJsonContent(self.__simulationDescription.path, f'relevant-electric-field-vector_{offsetName}.json', frontierElectricFieldVector)
