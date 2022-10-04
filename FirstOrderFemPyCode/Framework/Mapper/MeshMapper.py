
from typing import Any

from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh
from FirstOrderFemPyCode.Framework.Command.MeshContainer.ViewObject import ViewObject

class MeshMapper:
    @staticmethod
    def map(meshContainerFreeCAD: ViewObject.MeshContainerDataContainer) -> Mesh:
        if len(meshContainerFreeCAD.Group) != 1:
            raise Exception('Unexpected number of objects inside MeshContainer')
        
        meshFreeCAD = meshContainerFreeCAD.Group[0].Mesh
        mesh = Mesh()
        
        mesh.elements = meshFreeCAD.Facets
        mesh.points = meshFreeCAD.Points
        mesh.boundBox = meshFreeCAD.BoundBox
        
        return mesh
