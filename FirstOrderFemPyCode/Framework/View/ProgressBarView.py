from typing import Any, List

import FreeCAD
from FirstOrderFemPyCode.Framework.Service.UiLoaderServiceInterface import \
    UiLoaderServiceInterface
from FirstOrderFemPyCode.Framework.View.ProgressBarViewInterface import \
    ProgressBarViewInterface
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface
from FirstOrderFemPyCode.Framework.Command.Interface import ViewObjectInterface

if FreeCAD.GuiUp:
    from PySide import QtCore


class ProgressBarView(ProgressBarViewInterface):
    __view: Any
    __callback: ProgressBarViewInterface.CallbackInterface

    def __init__(
        self, 
        uiLoaderService: UiLoaderServiceInterface, 
        callback: ProgressBarViewInterface.CallbackInterface,
        obj: ViewObjectInterface.ObjectInterface = None,
        childs: List[ViewInterface] = None
    ):
        self.__view = uiLoaderService.load("ProgressBar")
        self.__view.btnCancel.clicked.connect(self.__onBtnCancelClicked)

        self.__view.setWindowFlags(
            self.__view.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint
        )

        self.__view.setWindowFlags(
            self.__view.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
        )

        self.__callback = callback

    def __onBtnCancelClicked(self, *args) -> None:
        self.reject()

    def accept(self) -> None:
        self.__callback.onAccept()

    def reject(self) -> None:
        self.__view.close()
        self.__callback.onReject()

    def closing(self) -> None:
        self.__view.close()
        self.__callback.onClose()

    def show(self) -> None:
        self.__view.show()

    def setProgress(self, progress: int) -> None:
        self.__view.progressBar.setValue(progress)

    def resetText(self) -> None:
        self.__view.label.setText('')

    def showText(self, text: str) -> None:
        self.__view.label.setText(text)

    def getText(self) -> str:
        return self.__view.label.text()

    def getProgress(self) -> int:
        return self.__view.progressBar.value()
