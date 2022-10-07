import abc
from typing import Dict


class RunSimulationRepositoryInterface:
    
    @abc.abstractmethod
    def writeNodeVoltages(self: 'RunSimulationRepositoryInterface', path: str, outputNameWithExtension: str, voltages: Dict[int, float]) -> None:
        raise NotImplementedError
