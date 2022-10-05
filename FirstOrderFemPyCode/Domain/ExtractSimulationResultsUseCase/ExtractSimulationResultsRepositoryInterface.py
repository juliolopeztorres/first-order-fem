import abc
from typing import Any, Dict, List, Optional

from FirstOrderFemPyCode.Domain.Model.SimulationDescription import \
    SimulationDescription


class ExtractSimulationResultsRepositoryInterface:

    @abc.abstractmethod
    def setSimulationInformation(self: 'ExtractSimulationResultsRepositoryInterface', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def extractInfoForVtk(self: 'ExtractSimulationResultsRepositoryInterface') -> List[Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def extractInfoForPlotElementsCenter(self: 'ExtractSimulationResultsRepositoryInterface') -> List[Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def extractInfoForPlotCartesianGrid(self: 'ExtractSimulationResultsRepositoryInterface') -> List[Any]:
        raise NotImplementedError
    
    @abc.abstractmethod
    def extractChargeInfo(self: 'ExtractSimulationResultsRepositoryInterface') -> Dict[str, List[Any]]:
        raise NotImplementedError
    
    @abc.abstractmethod
    def saveInfoToFile(self: 'ExtractSimulationResultsRepositoryInterface', info: List[Any]) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def saveChargeInfoToFile(self: 'ExtractSimulationResultsRepositoryInterface', chargeInfo: Dict[str, List[Any]]) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def exportToVtk(self: 'ExtractSimulationResultsRepositoryInterface', info: List[Any]) -> None:
        raise NotImplementedError
