from enum import Enum, auto, unique
import json
import math
from typing import Any, Dict, List, Optional

from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh
from FirstOrderFemPyCode.Domain.Model import EPSILON_0, MAP_INDICES
import numpy as np

import FirstOrderFemPyCode.Framework.Util as Util
import FreeCAD
import Draft

class Extractor:
    @unique
    class Plot(Enum):
        CARTESIAN_GRID = auto()
        ELEMENT_CENTER = auto()
        VTK = auto()
   
    __mesh: Mesh
    __elements: np.ndarray # List of Mesh.Facets
    
    __path: str
    
    __linearCoefficients: Dict[int, List[float]]
    __nodeVoltages: Dict[int, float]
    
    def __init__(self: 'Extractor', path: str, mesh: Mesh, nodeVoltages: Optional[Dict[int, float]]) -> None:
        self.__path = path
        
        self.__mesh = mesh
        self.__elements = np.array(mesh.elements)
        
        self.__nodeVoltages = nodeVoltages if nodeVoltages else self.__getNodeVoltages()

        self.__linearCoefficients = self.__getCoefficientDictForElements()

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

    def __getXY(self: 'Extractor', i: int, direction: int, element: Any) -> float:
        return element.Points[MAP_INDICES[i] - 1][direction] - element.Points[MAP_INDICES[MAP_INDICES[i]] - 1][direction]

    def __getY(self: 'Extractor', i: int, element: Any) -> float:
        return self.__getXY(i, 1, element)

    def __getX(self: 'Extractor', i: int, element: Any) -> float:
        return self.__getXY(i, 0, element)

    def __getK(self: 'Extractor', i: int, element: Any) -> float:
        points = element.Points

        initMapIndex = MAP_INDICES[i]

        return points[initMapIndex - 1][0] * points[MAP_INDICES[initMapIndex] - 1][1] - \
            points[MAP_INDICES[initMapIndex] - 1][0] * points[initMapIndex - 1][1]

    def __getVoltagesForElement(self: 'Extractor', element: Any) -> List[float]:
        return [self.__nodeVoltages[pointIndex + 1] for pointIndex in element.PointIndices]

    def __getCoefficientsForElement(self: 'Extractor', element: Any, voltages: List[float]) -> List[float]:
        # area = element.Area
        # Elements area does not get an extra sign from the determinant
        area = (1/2) * sum([self.__getK(i + 1, element) for i in range(3)])
        
        prefactor = 1/(2*area)
        
        a = prefactor * sum([self.__getK(i + 1, element) * voltages[i] for i in range(3)])
        # Units for `b` and `c` are V/mm
        b = prefactor * sum([self.__getY(i + 1, element) * voltages[i] for i in range(3)])
        c = -prefactor * sum([self.__getX(i + 1, element) * voltages[i] for i in range(3)])
        
        return [a, b, c]

    def __getCoefficientDictForElements(self: 'Extractor') -> Dict[int, List[float]]:
        result = {}
        
        for element in self.__elements:
            result[element.Index + 1] = self.__getCoefficientsForElement(element, self.__getVoltagesForElement(element))
        
        return result

    def __getVoltage(self: 'Extractor', point: List[float], linearCoefficients: List[float]):
        return linearCoefficients[0] + linearCoefficients[1] * point[0] + linearCoefficients[2] * point[1]

    def __getElectricFieldMagnitude(self: 'Extractor', linearCoefficients: List[float]) -> float:
        return math.sqrt(
            math.pow(linearCoefficients[1], 2) + math.pow(linearCoefficients[2], 2)
        )

    def __getCartesianGridValues(self: 'Extractor', pointsPerDirection: int = 25) -> List[Any]:
        # Loop over x-y map, find triangle belonging, get its index and estimate voltage
        x_max, y_max = self.__mesh.boundBox.XMax, self.__mesh.boundBox.YMax
        x_min, y_min = self.__mesh.boundBox.XMin, self.__mesh.boundBox.YMin

        results = []
        for x in np.linspace(x_min, x_max, pointsPerDirection):
            for y in np.linspace(y_min, y_max, pointsPerDirection):
                elementCandicate = [element for element in self.__elements if self.__pointInElement([x, y], element)]
                
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
                elementCoefficients = self.__linearCoefficients[elementCandicate[0].Index + 1]
                results.append(
                    {
                        'point': [x, y], 
                        'voltage': self.__getVoltage([x, y], elementCoefficients),
                        'E_mag': self.__getElectricFieldMagnitude(elementCoefficients) # V/mm
                    }
                )
                
        return results

    def __getElementsCenterValue(self: 'Extractor') -> List[Any]:
        results = []
        for element in self.__elements:
            x, y = element.InCircle[0][0:2]

            # Get Electric Field
            elementCoefficients = self.__linearCoefficients[element.Index + 1]
            results.append(
                {
                    'point': [x, y],
                    'voltage': self.__getVoltage([x, y], elementCoefficients), # V/mm
                    'E_mag': self.__getElectricFieldMagnitude(elementCoefficients)
                }
            )
            
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
            element = self.__elements[frontierElementIndex - 1]
            
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
        for element in self.__elements:
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
