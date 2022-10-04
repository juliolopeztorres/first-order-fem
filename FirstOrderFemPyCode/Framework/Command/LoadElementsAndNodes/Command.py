import os
from typing import Any, Dict, List, Tuple

import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.Interface import CommandInterface
import Draft

if FreeCAD.GuiUp:
    from PySide import QtCore
    import FreeCADGui


class Command(CommandInterface):
    __FREECAD_EMPTY_BOUNDARY_INDEX = 4294967295
    __MAP_INDICES = {
        1: 2,
        2: 3,
        3: 1
    }

    __COLOR_BLUE = (0.00, 1.00, 1.00)
    __COLOR_YELLOW = (1.00, 1.00, 0.00)

    def GetResources(self) -> Dict[str, str]:
        return {
            'Pixmap': os.path.join(Util.getModulePath(), "assets", "icons", "probes.png"),
            'MenuText': QtCore.QT_TRANSLATE_NOOP("LoadElementsAndNodes", "MENU_TEXT"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("LoadElementsAndNodes", "TOOLTIP")
        }

    def IsActive(self) -> bool:
        currentSelection: List[Any] = FreeCADGui.Selection.getSelection()

        return FreeCAD.ActiveDocument is not None \
            and len(currentSelection) == 1 \
            and currentSelection[0].isDerivedFrom('Mesh::Feature')

    def __cleanNodesAndBoundariesGroup(self: 'Command') -> None:
        try:
            boundariesGroup = Util.getObjectInDocumentByName('boundaries')
            boundariesGroup.removeObjectsFromDocument()

            Util.removeObjectFromActiveDocument('boundaries')

            nodesGroups = Util.getObjectInDocumentByName('nodes')
            nodesGroups.removeObjectsFromDocument()

            Util.removeObjectFromActiveDocument('nodes')
        except:
            pass

    def __addTextToGroup(
        self: 'Command',
        text: str,
        group: Any,
        position: FreeCAD.Vector,
        color: Tuple[float, float, float],
        fontSize: float
    ) -> None:
        textDraft: Any = Draft.make_text([text], placement=position)
        textDraft.Label = text
        textDraft.ViewObject.TextColor = color
        textDraft.ViewObject.FontSize = f'{fontSize} mm'

        group.addObject(textDraft)

    def __getSortedBoundaryNodes(self: 'Command', elements: List[Any]) -> List[Any]:
        boundNodes = []
        for element in elements:
            if not Command.__FREECAD_EMPTY_BOUNDARY_INDEX in element.NeighbourIndices:
                continue

            sideStartingNode = element.NeighbourIndices.index(
                Command.__FREECAD_EMPTY_BOUNDARY_INDEX)

            pointIndex1 = element.PointIndices[sideStartingNode] + 1
            pointIndex2 = element.PointIndices[Command.__MAP_INDICES[sideStartingNode + 1] - 1] + 1

            if not pointIndex1 in boundNodes:
                boundNodes.append(pointIndex1)

            if not pointIndex2 in boundNodes:
                boundNodes.append(pointIndex2)

        boundNodes.sort()

        return boundNodes

    def Activated(self) -> None:
        meshCandidate = FreeCADGui.Selection.getSelection()[0]

        mesh: Any = meshCandidate.Mesh
        elements: List[Any] = mesh.Facets
        nodes: List[Any] = mesh.Points

        self.__cleanNodesAndBoundariesGroup()

        estimatedFontSize = elements[0].InCircle[1]

        boundariesGroup = Util.addAndGetGroupInDocument('boundaries')
        nodesGroups = Util.addAndGetGroupInDocument('nodes')

        # To show Boundaries face indices index with updated color and size
        boundIndices = [face.Index for face in elements if 4294967295 in face.NeighbourIndices]
        boundIndices.sort()
        for boundIndex in boundIndices:
            self.__addTextToGroup(
                str(boundIndex + 1),
                boundariesGroup,
                elements[boundIndex].InCircle[0],
                Command.__COLOR_BLUE,
                estimatedFontSize
            )

        # Boundary nodes (Points)
        for boundNode in self.__getSortedBoundaryNodes(elements):
            self.__addTextToGroup(
                str(boundNode),
                nodesGroups,
                nodes[boundNode - 1].Vector,
                Command.__COLOR_YELLOW,
                estimatedFontSize
            )

        FreeCAD.ActiveDocument.recompute()
