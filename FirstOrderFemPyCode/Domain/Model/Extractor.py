from enum import Enum, auto, unique
import json
from typing import Any, Dict, List, Optional
from FirstOrderFemPyCode.Domain.Model.AbstractFemModel import AbstractFemModel

from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh
from FirstOrderFemPyCode.Domain.Model import EPSILON_0, MAP_INDICES
import numpy as np

import FirstOrderFemPyCode.Framework.Util as Util
import FreeCAD
import Draft

class Extractor(AbstractFemModel):
    @unique
    class Plot(Enum):
        CARTESIAN_GRID = auto()
        ELEMENT_CENTER = auto()
        VTK = auto()
   
    __path: str
    
    __linearCoefficients: Dict[int, List[float]]
    
    def __init__(self: 'Extractor', path: str, mesh: Mesh, nodeVoltages: Optional[Dict[int, float]]) -> None:
        super().__init__(mesh)
        self.__path = path
        
        self.nodeVoltages = nodeVoltages if nodeVoltages else self.__getNodeVoltages()

        self.__linearCoefficients = self._getCoefficientDictForElements()

    # TODO: This should be injected and non-optional
    def __getNodeVoltages(self: 'Extractor') -> Dict[int, float]:
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

    def __sign(self: 'Extractor', p1: List[float], p2: List[float], p3: List[float]) -> float:
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1]);

    def __pointInElement(self: 'Extractor', p: List[float], element: Any) -> bool:
        d1 = self.__sign(p, element.Points[0], element.Points[1])
        d2 = self.__sign(p, element.Points[1], element.Points[2])
        d3 = self.__sign(p, element.Points[2], element.Points[0])

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def __getPointVoltageAndEField(self: 'Extractor', x: float, y: float, elementId: int) -> Dict[str, Any]:
        elementCoefficients = self.__linearCoefficients[elementId]
        return {
                'point': [x, y], 
                'voltage': self._getVoltage([x, y], elementCoefficients),
                'E_mag': self._getElectricFieldMagnitude(elementCoefficients) # V/mm
            }

    def __getCartesianGridValues(self: 'Extractor', pointsPerDirection: int = 25) -> List[Any]:
        # Loop over x-y map, find triangle belonging, get its index and estimate voltage
        x_max, y_max = self._mesh.boundBox.XMax, self._mesh.boundBox.YMax
        x_min, y_min = self._mesh.boundBox.XMin, self._mesh.boundBox.YMin

        results = []
        for x in np.linspace(x_min, x_max, pointsPerDirection):
            for y in np.linspace(y_min, y_max, pointsPerDirection):
                elementCandicate = [element for element in self._elements if self.__pointInElement([x, y], element)]
                
                if len(elementCandicate) == 0:
                    results.append(
                        {
                            'point': [x, y], 
                            'voltage': 0.0,
                            'E_mag': 0.0 # V/mm
                        }
                    )
                    
                    continue

                # Does not matter if multiple elements are returned as the voltage is continuous
                # if len(elementCandicate) != 1:
                #     raise Exception(f"Unexpected number of candidates for point [{x}, {y}]")
                
                # Get Electric Field
                results.append(self.__getPointVoltageAndEField(x, y, elementCandicate[0].Index + 1))
                
        return results

    def __getElementsCenterValue(self: 'Extractor') -> List[Any]:
        results = []
        for element in self._elements:
            x, y = element.InCircle[0][0:2]

            # Get Electric Field
            results.append(self.__getPointVoltageAndEField(x, y, element.Index + 1))
            
        return results

    def __getCleanedGroup(self: 'Extractor', name: str) -> Any:
        try:
            group = Util.getObjectInDocumentByName(name)
            group.removeObjectsFromDocument()

            Util.removeObjectFromActiveDocument(name)
        except:
            pass

        return Util.addAndGetGroupInDocument(name)

    def __getFrontierElementsValues(self: 'Extractor', offsetName: str, frontierElements: List[int]) -> List[Any]:
        normalsGroup = self.__getCleanedGroup(f'normals_{offsetName}')
        
        frontierElementsValues = []
        for frontierElementIndex in frontierElements:
            coefficients = self.__linearCoefficients[frontierElementIndex]
            
            # Calculate the charge by
            # 1.- Get the vector of the frontier, normalize
            element = self._elements[frontierElementIndex - 1]
            
            sideStartingNode = element.NeighbourIndices.index(4294967295)
            
            vect = FreeCAD.Vector(element.Points[sideStartingNode]) - FreeCAD.Vector(element.Points[MAP_INDICES[sideStartingNode + 1] - 1])
            # Meters need to be considered
            elementSideLength = vect.Length * 1e-3
            
            if vect[2] != 0.0:
                raise Exception(f'Found side with non-zero offset. Element id {frontierElementIndex}')
            
            # vect[2] = 0.0
            vect.normalize()
            
            # 2.- Calculate 2D perpendicular, normalize
            normalVect = FreeCAD.Vector([-vect[1], +vect[0], vect[2]])
            normalVect.normalize()
            
            if vect.dot(normalVect) > 1e-15:
                raise Exception("Could not calculate normal vector for element " + str(frontierElementIndex))
                
            # 3.- Calculate dot operation with E_vector
            EVect = FreeCAD.Vector([-coefficients[1], -coefficients[2], vect[2]])
            chargeDensity = (EPSILON_0 * EVect * 1e3).dot(normalVect) # Pass E_vect from V/mm to V/m
            
            frontierElementsValues.append({
                'element': frontierElementIndex,
                'E_vector': list(EVect)[:2],
                'charge': chargeDensity * elementSideLength
            })
            
            normalVect.multiply(0.25)
            
            line = Draft.makeLine(element.InCircle[0], element.InCircle[0] + normalVect)
            
            line.ViewObject.EndArrow = True
            line.ViewObject.ArrowType = u"Arrow"
            line.ViewObject.ArrowSize = '0.02 mm'
            
            normalsGroup.addObject(line)
            
        FreeCAD.ActiveDocument.recompute()
            
        return frontierElementsValues

    def __getElementsElectricFieldVector(self: 'Extractor') -> List[Any]:
        results = []
        for element in self._elements:
            elementCoefficients = self.__linearCoefficients[element.Index + 1]
            results.append(
                {
                    'element': element.Index + 1,
                    'E_vector': (-elementCoefficients[1], -elementCoefficients[2])
                }
            )

        return results

    def writeMappedValuesToFile(self: 'Extractor', results: List[Any], outputFileName: str) -> None:
        with open(Util.joinPaths(self.__path, outputFileName), 'w') as output:
            json.dump(results, output)

        output.close()

    def extractPlotInfo(self: 'Extractor', plot: Plot = Plot.VTK, pointsPerDirection: int = 25) -> List[Any]:
        if plot == Extractor.Plot.VTK:
            results = self.__getElementsElectricFieldVector()
        elif plot == Extractor.Plot.CARTESIAN_GRID:
            results = self.__getCartesianGridValues(pointsPerDirection)
        elif plot == Extractor.Plot.ELEMENT_CENTER:
            results = self.__getElementsCenterValue()
        else:
            raise Exception(f'Unexpected plot type entered {plot}')

        self.writeMappedValuesToFile(results, 'plot-info.json')
        
        return results

    def extractChargeOnFrontier(self: 'Extractor', offsetName: str, frontierElements: List[int]) -> float:
        frontierElectricFieldVector = self.__getFrontierElementsValues(offsetName, frontierElements)

        self.writeMappedValuesToFile(frontierElectricFieldVector, f'relevant-electric-field-vector_{offsetName}.json')

        return sum([values['charge'] for values in frontierElectricFieldVector])
