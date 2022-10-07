from typing import Any, Dict
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription
from FirstOrderFemPyCode.Domain.Model.Simulation import Simulation
from FirstOrderFemPyCode.Domain.RunSimulationUseCase.RunSimulationRepositoryInterface import RunSimulationRepositoryInterface

class RunSimulationUseCase:
    __repository: RunSimulationRepositoryInterface
    
    def __init__(self: 'RunSimulationUseCase', repository: RunSimulationRepositoryInterface) -> None:
        self.__repository = repository
    
    def run(self: 'RunSimulationUseCase', simulationDescription: SimulationDescription) -> Simulation:
        mesh = simulationDescription.mesh

        simulation = Simulation(mesh, simulationDescription.prescribedNodes)
        simulation.solve()

        self.__repository.writeNodeVoltages(simulationDescription.path, 'solution.json', simulation.nodeVoltages)

        return simulation
