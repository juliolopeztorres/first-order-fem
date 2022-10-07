from enum import Enum, auto, unique
from typing import Any, Dict, List
from FirstOrderFemPyCode.Domain.Model.AbstractFemModel import AbstractFemModel

from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh
from FirstOrderFemPyCode.Domain.Model import EPSILON_0, MAP_INDICES
import numpy as np

import FirstOrderFemPyCode.Framework.Util as Util
import FreeCAD
import Draft

class ExtractorService(AbstractFemModel):
    @unique
    class Plot(Enum):
        CARTESIAN_GRID = auto()
        ELEMENT_CENTER = auto()
        VTK = auto()
   
    __linearCoefficients: Dict[int, List[float]]
    
    def __init__(self: 'ExtractorService', mesh: Mesh, nodeVoltages: Dict[int, float]) -> None:
        super().__init__(mesh)
        
        self.nodeVoltages = nodeVoltages

        self.__linearCoefficients = self._getCoefficientDictForElements()

    def __sign(self: 'ExtractorService', p1: List[float], p2: List[float], p3: List[float]) -> float:
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1]);

    def __pointInElement(self: 'ExtractorService', p: List[float], element: Any) -> bool:
        d1 = self.__sign(p, element.Points[0], element.Points[1])
        d2 = self.__sign(p, element.Points[1], element.Points[2])
        d3 = self.__sign(p, element.Points[2], element.Points[0])

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def __getPointVoltageAndEField(self: 'ExtractorService', x: float, y: float, elementId: int) -> Dict[str, Any]:
        elementCoefficients = self.__linearCoefficients[elementId]
        return {
                'point': [x, y], 
                'voltage': self._getVoltage([x, y], elementCoefficients),
                'E_mag': self._getElectricFieldMagnitude(elementCoefficients) # V/mm
            }

    def __getCartesianGridValues(self: 'ExtractorService', pointsPerDirection: int = 25) -> List[Any]:
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

    def __getElementsCenterValue(self: 'ExtractorService') -> List[Any]:
        results = []
        for element in self._elements:
            x, y = element.InCircle[0][0:2]

            # Get Electric Field
            results.append(self.__getPointVoltageAndEField(x, y, element.Index + 1))
            
        return results

    def __getCleanedGroup(self: 'ExtractorService', name: str) -> Any:
        try:
            group = Util.getObjectInDocumentByName(name)
            group.removeObjectsFromDocument()

            Util.removeObjectFromActiveDocument(name)
        except:
            pass

        return Util.addAndGetGroupInDocument(name)

    def __getElementsElectricFieldVector(self: 'ExtractorService') -> List[Any]:
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

    def extractPlotInfo(self: 'ExtractorService', plot: Plot, pointsPerDirection: int = 25) -> List[Any]:
        if plot == ExtractorService.Plot.VTK:
            plotInfo = self.__getElementsElectricFieldVector()
        elif plot == ExtractorService.Plot.CARTESIAN_GRID:
            plotInfo = self.__getCartesianGridValues(pointsPerDirection)
        elif plot == ExtractorService.Plot.ELEMENT_CENTER:
            plotInfo = self.__getElementsCenterValue()
        else:
            raise Exception(f'Unexpected plot type entered {plot}')

        return plotInfo

    def getFrontierElementsValues(self: 'ExtractorService', offsetName: str, frontierElements: List[int]) -> List[Any]:       
        frontierElementsValues = []
        lines: List[Any] = []
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
            
            lines.append(line)

        normalsGroup = self.__getCleanedGroup(f'normals_{offsetName}')
        normalsGroup.addObjects(lines)

        FreeCAD.ActiveDocument.recompute()
            
        return frontierElementsValues
