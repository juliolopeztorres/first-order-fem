import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any, List, Tuple, Type

import FreeCAD
from FirstOrderFemPyCode.Framework.Command.Interface import ViewProviderInterface

if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui


def removeFolder(folderFullPath: str) -> None:
    if os.path.exists(folderFullPath):
        shutil.rmtree(folderFullPath)


def getModulePath():
    return os.path.dirname(__file__) + '\\..\\..\\'


def joinPathsToCurrent(*paths):
    return os.path.join(getModulePath(), *paths)


def joinPaths(*paths):
    return os.path.join(*paths)


def getSimulationOutputFolderPath(simulationPath: str) -> str:
    return joinPaths(
        os.path.dirname(simulationPath),
        Path(simulationPath).stem
    )


def addObjectProperty(obj, prop, init_val, type, *args):
    added = False
    if prop not in obj.PropertiesList:
        added = obj.addProperty(type, prop, *args)

    if type == "App::PropertyQuantity":
        setattr(obj, prop, FreeCAD.Units.Unit(init_val))

    if added:
        setattr(obj, prop, init_val)
        return True

    return False


def showErrorDialog(msg: str):
    QtGui.QApplication.restoreOverrideCursor()
    if FreeCAD.GuiUp:
        QtGui.QMessageBox.critical(
            None,
            FreeCAD.Qt.translate("Util", "ERROR_DIALOG_TITLE"),
            msg
        )
        return

    FreeCAD.Console.PrintError('ERROR: ' + msg + "\n")


def showInfoDialog(msg: str):
    QtGui.QApplication.restoreOverrideCursor()
    if FreeCAD.GuiUp:
        QtGui.QMessageBox.information(
            None,
            FreeCAD.Qt.translate("Util", "ERROR_DIALOG_TITLE"),
            msg
        )
        return

    FreeCAD.Console.PrintMessage('INFO: ' + msg + "\n")


def openFileManager(path):
    path = os.path.abspath(path)

    if platform.system() == 'MacOS':
        subprocess.Popen(['open', '--', path])
    elif platform.system() == 'Linux':
        subprocess.Popen(['xdg-open', path])
    elif platform.system() == 'Windows':
        subprocess.Popen(['explorer', path])


class InputEvent:
    def connect(self, *args, **kwargs) -> None:
        pass


def getInputEventsForWidget(widget: Any) -> Tuple[InputEvent, InputEvent, InputEvent, InputEvent, InputEvent]:
    class Filter(QtCore.QObject):
        clicked = QtCore.Signal()
        focusOut = QtCore.Signal()
        focusIn = QtCore.Signal()
        enterClicked = QtCore.Signal()

        debounce: QtCore.QTimer
        debounceTextChanged = QtCore.Signal()

        def __init__(self, widget, *args, **kwargs) -> None:
            super().__init__(widget, *args, **kwargs)

            self.debounce = QtCore.QTimer()

            self.debounce.setInterval(750)
            self.debounce.setSingleShot(True)
            self.debounce.timeout.connect(
                lambda: self.debounceTextChanged.emit()
            )

            widget.textChanged.connect(self.debounce.start)

        def eventFilter(self, obj, event):
            if obj == widget and event.type() == QtCore.QEvent.MouseButtonRelease and obj.rect().contains(event.pos()):
                self.clicked.emit()
                return False

            if (obj == widget and event.type() == QtCore.QEvent.FocusOut):
                self.focusOut.emit()
                return False

            if (obj == widget and event.type() == QtCore.QEvent.FocusIn):
                self.focusIn.emit()
                return False

            if (obj == widget and event.type() == QtCore.QEvent.KeyPress and event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]):
                self.enterClicked.emit()
                return False

            return False

    filter = Filter(widget)

    widget.installEventFilter(filter)
    return (filter.clicked, filter.focusIn, filter.focusOut, filter.enterClicked, filter.debounceTextChanged)


def addGroupToDocument(name: str) -> Any:
    return FreeCAD.activeDocument().addObject('App::DocumentObjectGroup', name)


def getObjectInDocumentByName(name: str) -> Any:
    object = FreeCAD.ActiveDocument.getObject(name)
    if not object:
        raise Exception(
            'An object with the name {} could not be retrieved'.format(name)
        )

    return object


def addAndGetGroupInDocument(name: str) -> Any:
    addGroupToDocument(name)

    return getObjectInDocumentByName(name)


def getDataObjectsWithViewObjectProxyInstance(objects: List[Any], className: Type[ViewProviderInterface]) -> List[Any]:
    # Returns -> List[instances of DataContainer associated to the given ViewProvider class]
    return [
        object for object in objects
        if hasattr(object, 'ViewObject') and hasattr(object.ViewObject, 'Proxy')
        and isinstance(object.ViewObject.Proxy, className)
    ]


def removeObjectFromActiveDocument(name: str) -> None:
    FreeCAD.ActiveDocument.removeObject(name)

def getCleanedGroup(name: str) -> Any:
    try:
        group = getObjectInDocumentByName(name)
        group.removeObjectsFromDocument()

        removeObjectFromActiveDocument(name)
    except:
        pass

    return addAndGetGroupInDocument(name)
