from typing import Any, Dict, Optional
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsUseCase import ExtractSimulationResultsUseCase
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription
from FirstOrderFemPyCode.Domain.Model.Simulation import Simulation
from FirstOrderFemPyCode.Domain.RunSimulationUseCase.RunSimulationRepositoryInterface import RunSimulationRepositoryInterface

class RunSimulationUseCase:
    __repository: RunSimulationRepositoryInterface
    __extractSimulationResultsUseCase: ExtractSimulationResultsUseCase
    
    def __init__(self: 'RunSimulationUseCase', repository: RunSimulationRepositoryInterface, extractSimulationResultsUseCase: ExtractSimulationResultsUseCase) -> None:
        self.__repository = repository
        self.__extractSimulationResultsUseCase = extractSimulationResultsUseCase
    
    def run(self: 'RunSimulationUseCase', simulationDescription: SimulationDescription) -> Dict[str, Any]:
        mesh = simulationDescription.mesh

        simulation = Simulation(mesh, simulationDescription.prescribedNodes)#, simulationDescription.path)
        simulation.solve()

        self.__repository.writeNodeVoltages(simulationDescription.path, 'solution.json', simulation.nodeVoltages)

        chargeInfo = self.__extractSimulationResultsUseCase.extract(simulationDescription, simulation.nodeVoltages)

        return {
            'energy': simulation.energy,
            'nodeVoltages': simulation.nodeVoltages,
            'chargeInfo': chargeInfo
        }
