from typing import Dict, Optional
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
    
    def run(self: 'RunSimulationUseCase', simulationDescription: SimulationDescription) -> Optional[Dict[int, float]]:
        mesh = simulationDescription.mesh

        simulation = Simulation(mesh, simulationDescription.prescribedNodes)#, simulationDescription.path)
        simulation.solve()
        # print('Solution')
        print(f'Energy:{simulation.energy}J\n')
        # solutionStr = 'V\n'.join([str(solutioni) for solutioni in simulation.solution]) + 'V\n'
        # print(f'Free Nodes:\n{solutionStr}')

        self.__repository.writeNodeVoltages(simulationDescription.path, 'solution.json', simulation.nodeVoltages)

        self.__extractSimulationResultsUseCase.extract(simulationDescription, simulation.nodeVoltages)

        return simulation.nodeVoltages
