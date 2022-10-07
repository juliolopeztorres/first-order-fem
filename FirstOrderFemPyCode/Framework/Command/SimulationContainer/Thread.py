from typing import Any, Dict
from FirstOrderFemPyCode.Domain.RunSimulationUseCase.RunSimulationUseCase import RunSimulationUseCase
from FirstOrderFemPyCode.Framework.Command.SimulationContainer.ViewObject import ViewObject
from FirstOrderFemPyCode.Framework.Mapper.SimulationDescriptionMapper import SimulationDescriptionMapper
import FreeCAD
import time
import FirstOrderFemPyCode.Framework.Util as Util
from pathlib import Path


if FreeCAD.GuiUp:
    from PySide import QtCore
    from PySide.QtCore import QObject, QThread

class ThreadOutput(object):
    simulationOutput: Dict[str, Any]
    
    def __init__(self, simulationOutput: Dict[str, Any] = {}) -> None:
        self.simulationOutput = simulationOutput

class Signals(QObject):
    error = QtCore.Signal(str)
    finished = QtCore.Signal(bool, ThreadOutput)
    status = QtCore.Signal(str)
    update = QtCore.Signal(int)


class Thread(QThread):

    signals: Signals = Signals()
    runSimulationUseCase: RunSimulationUseCase
    object: ViewObject.SimulationContainerDataContainer

    def __cleanAndCreateSimulationFolder(self, path: str) -> None:
        Util.removeFolder(path)
        Path(path).mkdir(exist_ok=True, parents=True)

    def __updateProgression(self, progress: int) -> None:
        self.signals.update.emit(progress)

    def __runSimulationScenario(self) -> Dict[str, Any]:
        self.updateStatus(5, 'Mapping simulation entry data...')
        
        simulationDescription = SimulationDescriptionMapper.map(
            self.object, 
            Util.getSimulationOutputFolderPath(FreeCAD.ActiveDocument.FileName)
        )
        
        self.updateStatus(20, 'Cleaning simulation output folder...')
        
        self.__cleanAndCreateSimulationFolder(simulationDescription.path)
        
        self.updateStatus(40, 'Running simulation...')

        simulation = self.runSimulationUseCase.run(simulationDescription)

        return {
            'energy': simulation.energy,
            'nodeVoltages': simulation.nodeVoltages,
            'simulationDescription': simulationDescription,
        }

    def run(self) -> None:
        try:
            self.signals.finished.emit(True, ThreadOutput(self.__runSimulationScenario()))
        except Exception as e:
            list = range(4)
            for i in list:
                self.signals.error.emit(
                    "<b style='color: red'>ERROR: {} <br/> Closing in {:n}...</b>".format(str(e), len(list) - i))
                time.sleep(1)
            self.signals.finished.emit(False, ThreadOutput())

    def updateStatus(self, progression: int, status: str) -> None:
        self.signals.status.emit(status)
        self.__updateProgression(progression)
