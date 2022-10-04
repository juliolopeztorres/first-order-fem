import abc
from typing import Dict, Optional

from FirstOrderFemPyCode.Domain.Model.SimulationDescription import \
    SimulationDescription


class ExtractSimulationResultsRepositoryInterface:

    @abc.abstractmethod
    def setSimulationInformation(self: 'ExtractSimulationResultsRepositoryInterface', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def extractInfoForVtk(self: 'ExtractSimulationResultsRepositoryInterface') -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def extractInfoForPlotElementsCenter(self: 'ExtractSimulationResultsRepositoryInterface') -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def extractInfoForPlotCartesianGrid(self: 'ExtractSimulationResultsRepositoryInterface') -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def extractChargeInfo(self: 'ExtractSimulationResultsRepositoryInterface') -> None:
        raise NotImplementedError
