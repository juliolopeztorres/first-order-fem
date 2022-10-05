import json
from typing import Any, Dict, List, Optional

import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Data.ExtractorService import ExtractorService
from FirstOrderFemPyCode.Data.VtkService import VtkService
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsRepositoryInterface import \
    ExtractSimulationResultsRepositoryInterface
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import \
    SimulationDescription
from FirstOrderFemPyCode.Domain.RunSimulationUseCase.RunSimulationRepositoryInterface import \
    RunSimulationRepositoryInterface


class DataRepository(RunSimulationRepositoryInterface, ExtractSimulationResultsRepositoryInterface):
    __simulationDescription: SimulationDescription
    __nodeVoltages: Dict[int, float]
    __extractorService: ExtractorService
    __vtkService: VtkService
    
    def __getNodeVoltages(self: 'DataRepository', path: str, fileNameWithExtension: str) -> Dict[int, float]:
        voltages = {}

        try:
            solutionRead = json.loads(
                open(Util.joinPaths(path, fileNameWithExtension), 'r').read()
            )
            
            for nodeIndex, voltaje in solutionRead.items():
                voltages[int(nodeIndex)] = voltaje

        except:
            raise Exception('No solution file was found')

        return voltages

    def __writeJsonContent(self: 'DataRepository', path: str, outputNameWithExtension: str, content: Any) -> None:
        with open(Util.joinPaths(path, outputNameWithExtension), 'w') as outfile:
            json.dump(content, outfile)

        outfile.close()

    def writeNodeVoltages(self: 'DataRepository', path: str, outputNameWithExtension: str, voltages: Dict[int, float]) -> None:
        self.__writeJsonContent(path, outputNameWithExtension, voltages)

    def setSimulationInformation(self: 'DataRepository', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        self.__simulationDescription = simulationDescription
        self.__nodeVoltages = nodeVoltages if nodeVoltages else self.__getNodeVoltages(simulationDescription.path, 'solution.json')
        
        self.__extractorService = ExtractorService(simulationDescription.mesh, self.__nodeVoltages)
        self.__vtkService = VtkService(self.__simulationDescription)

    def extractInfoForVtk(self: 'DataRepository') -> List[Any]:
        return self.__extractorService.extractPlotInfo(ExtractorService.Plot.VTK)

    def extractInfoForPlotElementsCenter(self: 'DataRepository') -> List[Any]:
        return self.__extractorService.extractPlotInfo(ExtractorService.Plot.ELEMENT_CENTER)
        
    def extractInfoForPlotCartesianGrid(self: 'DataRepository') -> List[Any]:
        return self.__extractorService.extractPlotInfo(ExtractorService.Plot.CARTESIAN_GRID, self.__simulationDescription.exportOptions.pointsPerDirection)

    def extractChargeInfo(self: 'DataRepository') -> Dict[str, List[Any]]:
        frontierInfo: Dict[str, List[Any]] = {}
        
        for frontierElementsGroupName, elements in self.__simulationDescription.frontierElementsGroups.items():
            frontierInfo[frontierElementsGroupName] = self.__extractorService.getFrontierElementsValues(frontierElementsGroupName, elements)
        
        return frontierInfo

    def saveInfoToFile(self: 'DataRepository', info: List[Any]) -> None:
        self.__writeJsonContent(self.__simulationDescription.path, 'plot-info.json', info)
    
    def saveChargeInfoToFile(self: 'DataRepository', chargeInfo: Dict[str, List[Any]]) -> None:
        for offsetName, frontierElectricFieldVector in chargeInfo.items():
            self.__writeJsonContent(self.__simulationDescription.path, f'relevant-electric-field-vector_{offsetName}.json', frontierElectricFieldVector)
    
    def exportToVtk(self: 'DataRepository', info: List[Any]) -> None:
        self.__vtkService.export(self.__nodeVoltages, info)
