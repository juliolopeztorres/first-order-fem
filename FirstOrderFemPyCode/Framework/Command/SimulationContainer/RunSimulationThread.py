from typing import Any, Dict
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsUseCase import ExtractSimulationResultsUseCase
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


class RunSimulationThread(QThread):
    signals: Signals
    runSimulationUseCase: RunSimulationUseCase
    extractSimulationResultsUseCase: ExtractSimulationResultsUseCase
    object: ViewObject.SimulationContainerDataContainer

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.signals = Signals()

    def __cleanAndCreateSimulationFolder(self, path: str) -> None:
        Util.removeFolder(path)
        Path(path).mkdir(exist_ok=True, parents=True)

    def __updateProgression(self, progress: int) -> None:
        self.signals.update.emit(progress)

    def __runSimulationScenario(self) -> Dict[str, Any]:
        self.updateStatus(5, FreeCAD.Qt.translate("SimulationContainer", "RUN_SIMULATION_THREAD_MAPPING_SIMULATION_DATA"))
        
        simulationDescription = SimulationDescriptionMapper.map(
            self.object, 
            Util.getSimulationOutputFolderPath(FreeCAD.ActiveDocument.FileName)
        )
        
        self.updateStatus(20, FreeCAD.Qt.translate("SimulationContainer", "RUN_SIMULATION_THREAD_CLEAN_SIMULATION_FOLDER"))
        
        self.__cleanAndCreateSimulationFolder(simulationDescription.path)
        
        self.updateStatus(40, FreeCAD.Qt.translate("SimulationContainer", "RUN_SIMULATION_THREAD_RUNNING_SIMULATION"))

        simulation = self.runSimulationUseCase.run(simulationDescription)

        self.updateStatus(50, FreeCAD.Qt.translate("SimulationContainer", "RUN_SIMULATION_THREAD_EXTRACTING_INFORMATION"))

        extractedInfo = self.extractSimulationResultsUseCase.extract(simulationDescription, simulation.nodeVoltages)
        
        self.updateStatus(60, FreeCAD.Qt.translate("SimulationContainer", "RUN_SIMULATION_THREAD_OPENING_OUTPUT_FOLDER"))

        Util.openFileManager(simulationDescription.path)

        self.updateStatus(80, FreeCAD.Qt.translate("SimulationContainer", "RUN_SIMULATION_THREAD_RETURNING"))

        return {
            'energy': simulation.energy,
            'nodeVoltages': simulation.nodeVoltages,
            'simulationDescription': simulationDescription,
            'extractedInfo': extractedInfo
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
