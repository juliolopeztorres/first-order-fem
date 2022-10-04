import json
from typing import Any, Dict

import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Domain.RunSimulationUseCase.RunSimulationRepositoryInterface import \
    RunSimulationRepositoryInterface


class DataRepository(RunSimulationRepositoryInterface):

    def __writeJsonContent(self: 'DataRepository', path: str, outputNameWithExtension: str, content: Any) -> None:
        with open(Util.joinPaths(path, outputNameWithExtension), 'w') as outfile:
            json.dump(content, outfile)

        outfile.close()

    def writeNodeVoltages(self: 'DataRepository', path: str, outputNameWithExtension: str, voltages: Dict[int, float]) -> None:
        self.__writeJsonContent(path, outputNameWithExtension, voltages)
