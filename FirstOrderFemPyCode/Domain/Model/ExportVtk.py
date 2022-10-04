from typing import Any, Dict, List, Optional, Tuple
from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh
from pyevtk.vtk import VtkFile, VtkUnstructuredGrid, VtkTriangle
import numpy as np
import FirstOrderFemPyCode.Framework.Util as Util
import json
from FirstOrderFemPyCode.Framework.Container import config
import subprocess

class ExportVtk:
    __path: str
    
    def __init__(self: 'ExportVtk', path: str) -> None:
        self.__path = path
    
    # These two functions are taken from original 'evtk.hl' module without changes.
    def __addDataToFile(self: 'ExportVtk', vtkFile, cellData, pointData):
        # Point data
        if pointData is not None:
            keys = pointData.keys()
            vtkFile.openData("Point", scalars=list(keys)[0])
            for key in keys:
                data = pointData[key]
                vtkFile.addData(key, data)
            vtkFile.closeData("Point")

        # Cell data
        if cellData is not None:
            keys = cellData.keys()
            vtkFile.openData("Cell", scalars=list(keys)[0])
            for key in keys:
                data = cellData[key]
                vtkFile.addData(key, data)
            vtkFile.closeData("Cell")

    def __appendDataToFile(self: 'ExportVtk', vtkFile, cellData, pointData):
        # Append data to binary section
        if pointData is not None:
            keys = pointData.keys()
            for key in keys:
                data = pointData[key]
                vtkFile.appendData(data)

        if cellData is not None:
            keys = cellData.keys()
            for key in keys:
                data = cellData[key]
                vtkFile.appendData(data)

    def __triangle_faces_to_VTK(self: 'ExportVtk', filename, x, y, z, faces, point_data, cell_data):
        vertices = (x, y, z)

        w = VtkFile(filename, VtkUnstructuredGrid)
        w.openGrid()
        w.openPiece(npoints=len(x), ncells=len(faces))
        w.openElement("Points")
        w.addData("Points", vertices)
        w.closeElement("Points")

        # Create some temporary arrays to write grid topology.
        ncells = len(faces)
        # Index of last node in each cell.
        offsets = np.arange(start=3, stop=3*(ncells + 1),
                            step=3, dtype='uint32')
        # Connectivity as unrolled array.
        connectivity = faces.reshape(ncells*3).astype('int32')
        cell_types = np.ones(ncells, dtype='uint8')*VtkTriangle.tid

        w.openElement("Cells")
        w.addData("connectivity", connectivity)
        w.addData("offsets", offsets)
        w.addData("types", cell_types)
        w.closeElement("Cells")

        self.__addDataToFile(w, cellData=cell_data, pointData=point_data)

        w.closePiece()
        w.closeGrid()

        w.appendData(vertices)
        w.appendData(connectivity).appendData(offsets).appendData(cell_types)

        self.__appendDataToFile(w, cellData=cell_data, pointData=point_data)

        w.save()
        return w.getFileName()

    def __getOrderedListFromDictWithIntegerKeys(self: 'ExportVtk', input: Dict[int, Any]) -> List[Any]:
        output = []
        for index in range(len(input)):
            output.append(input[index + 1])

        return output

    def __getElementEVector(self: 'ExportVtk') -> List[Any]:
        try:
            return json.loads(
                open(Util.joinPaths(self.__path, "plot-info.json"), 'r').read()
            )
        except Exception as e:
            raise Exception('No relevant electric field info file was found')

    def __mapElementEVector(self: 'ExportVtk', EVector: List[Any]) -> Dict[int, Tuple[float, float, float]]:
        EVectorMapped = {}
        
        for values in EVector:
            EVectorMapped[values['element']] = (values['E_vector'][0], values['E_vector'][1], 0.0)

        return EVectorMapped

    def __getNodeVoltages(self: 'ExportVtk') -> Dict[int, float]:
        voltages = {}

        try:
            solutionRead = json.loads(
                open(Util.joinPaths(self.__path, 'solution.json'), 'r').read()
            )
            
            for nodeIndex, voltaje in solutionRead.items():
                voltages[int(nodeIndex)] = voltaje

        except:
            raise Exception('No solution file was found')

        return voltages

    def run(self: 'ExportVtk', mesh: Mesh, voltages: Optional[Dict[int, float]], EVector: Optional[List[Any]], open: bool = True) -> None:
        voltages = voltages if voltages else self.__getNodeVoltages()
        
        EVectorOrdered = np.array(self.__getOrderedListFromDictWithIntegerKeys(
            self.__mapElementEVector(EVector if EVector else self.__getElementEVector()))
        )

        vertices = [np.array(list(point.Vector))for point in mesh.points]

        outputPath = Util.joinPaths(self.__path, "paraview-info")
        self.__triangle_faces_to_VTK(
            outputPath,
            x=np.array([v[0] for v in vertices]), 
            y=np.array([v[1] for v in vertices]), 
            z=np.array([v[2] for v in vertices]),
            faces=np.array([np.array(element.PointIndices) for element in mesh.elements]),
            point_data={'voltages': np.array(self.__getOrderedListFromDictWithIntegerKeys(voltages))},
            cell_data={'E_element': (np.array(EVectorOrdered[:, 0]), np.array(EVectorOrdered[:, 1]), np.array(np.zeros(len(mesh.elements))))}
        )
        
        if open and config('PARAVIEWPATH'):
            subprocess.Popen([config('PARAVIEWPATH'), outputPath + '.vtu'])
