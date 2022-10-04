import unittest
from typing import Any, Dict, List, Union
from glob import glob
from os import remove
from json import loads
from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh

# TODO: Check mock usage with Framework layer
import FreeCAD
import FirstOrderFemPyCode.Framework.Util as Util

class TestAbstractSimulation(unittest.TestCase):
    PATH = Util.joinPathsToCurrent('FirstOrderFemPyCodeTest', 'SimulationTestsOutput')
    _mesh: Mesh
    _nodeVoltages: Dict[int, float]
    
    def setUp(self) -> None:
        FreeCAD.openDocument(self._getTestFilePath('capacitor.FCStd'))
        
        meshFreeCAD = Util.getObjectInDocumentByName('Mesh').Mesh
        self._mesh = Mesh()
        
        self._mesh.elements = meshFreeCAD.Facets
        self._mesh.points = meshFreeCAD.Points
        self._mesh.boundBox = meshFreeCAD.BoundBox
        
        self._nodeVoltages = {}
        for nodeIndex, voltage in self._readFile(
            self._getTestFilePath('capacitor-solution.json'), 
            'Could not retrieve solution file'
        ).items(): # type: ignore
            self._nodeVoltages[int(nodeIndex)] = voltage

    def tearDown(self) -> None:
        if FreeCAD.ActiveDocument:
            FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)

    @classmethod
    def setUpClass(cls):
        # Try to clean output folder for each test
        files = glob(TestAbstractSimulation._getOutputFilePath('*'))
        
        for file in files:
            if '.gitkeep' in file:
                continue
            
            remove(file)

    @staticmethod
    def _getOutputFilePath(filename: str) -> str:
        return Util.joinPaths(TestAbstractSimulation.PATH, filename)
    
    @staticmethod
    def _getTestFilePath(filename: str) -> str:
        return Util.joinPathsToCurrent('FirstOrderFemPyCodeTest', 'MockCapacitorSimulation', filename)
    
    def _readFile(self, filename: str, failMessage: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        try:
            return loads(open(filename, 'r').read())
        except:
            self.fail(failMessage)
