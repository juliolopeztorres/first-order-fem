import os
from typing import Any

import FreeCAD
from FirstOrderFemPyCode.Framework.Service.UiLoaderServiceInterface import UiLoaderServiceInterface
from FirstOrderFemPyCode.Framework import Util

if FreeCAD.GuiUp:
    import FreeCADGui


class UiLoaderService(UiLoaderServiceInterface):

    def load(self, uiFileName: str) -> Any:
        return FreeCADGui.PySideUic.loadUi(os.path.join(
            Util.getModulePath(), 'assets', 'ui', "{}.ui".format(uiFileName)
        ))

    def getAnimationPath(self, fileName: str) -> Any:
        return os.path.join(
            Util.getModulePath(), 'assets', 'icons', "{}.gif".format(fileName)
        )
