from typing import Any, List


class Mesh:
    elements: List[Any] # FreeCAD.Mesh.Facets
    points: List[Any] # FreeCAD.Mesh.Points
    boundBox: Any # FreeCAD.Mesh.BoundBox
