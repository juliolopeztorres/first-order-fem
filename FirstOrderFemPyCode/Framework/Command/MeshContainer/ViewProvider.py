import os
from typing import Optional
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface

import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.MeshContainer.ViewObject import ViewObject
from FirstOrderFemPyCode.Framework.Command.Interface import ViewProviderInterface
from FirstOrderFemPyCode.Framework.Container import Container, View

if FreeCAD.GuiUp:
    import FreeCADGui


class ViewProvider(ViewProviderInterface, ViewInterface.CallbackInterface):
    __viewObject: ViewObject
    __view: Optional[ViewInterface] = None

    def __init__(self, vobj: ViewObject):
        vobj.Proxy = self

    def getIcon(self) -> str:
        return os.path.join(Util.getModulePath(), "assets", "icons", "mesh.png")

    def attach(self, vobj: ViewObject) -> None:
        self.__viewObject = vobj

    def doubleClicked(self, vobj: ViewObject) -> bool:
        # doc = FreeCADGui.getDocument(vobj.Object.Document)

        # if not doc.getInEdit():
        #     doc.setEdit(vobj.Object.Name)

        return True

    def setEdit(self, vobj: ViewObject, mode) -> bool:
        FreeCADGui.Selection.clearSelection()

        # self.__view: ViewInterface = Container.getView(
        #     View.MY_VIEW,
        #     self,
        #     vobj.Object
        # )

        if self.__view:
            # self.__view.loadData(self.__optionsModel)
            FreeCADGui.Control.showDialog(self.__view)

        return True

    def unsetEdit(self, vobj: ViewObject, mode) -> None:
        FreeCADGui.Control.closeDialog()

    def onAccept(self) -> None:
        FreeCADGui.ActiveDocument.resetEdit()

    def onReject(self) -> None:
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()

    def onClose(self) -> None:
        pass
