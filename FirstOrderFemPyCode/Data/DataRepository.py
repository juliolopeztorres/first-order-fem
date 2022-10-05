import json
from typing import Any, Dict

import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Domain.RunSimulationUseCase.RunSimulationRepositoryInterface import \
    RunSimulationRepositoryInterface


class DataRepository(RunSimulationRepositoryInterface):
    def _getNodeVoltages(self: 'DataRepository', path: str, fileNameWithExtension: str) -> Dict[int, float]:
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

    def _writeJsonContent(self: 'DataRepository', path: str, outputNameWithExtension: str, content: Any) -> None:
        with open(Util.joinPaths(path, outputNameWithExtension), 'w') as outfile:
            json.dump(content, outfile)

        outfile.close()

    def writeNodeVoltages(self: 'DataRepository', path: str, outputNameWithExtension: str, voltages: Dict[int, float]) -> None:
        self._writeJsonContent(path, outputNameWithExtension, voltages)
