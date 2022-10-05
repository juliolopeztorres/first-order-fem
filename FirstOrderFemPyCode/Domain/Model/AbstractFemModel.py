from abc import ABC
import math
from typing import Any, Dict, List
from FirstOrderFemPyCode.Domain.Model import EPSILON_0, MAP_INDICES
from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh
import numpy as np


class AbstractFemModel(ABC):
    _mesh: Mesh
    _elements: np.ndarray # List of FreeCAD Mesh.Facets
    nodeVoltages: Dict[int, float] = {}

    def __init__(self, mesh: Mesh) -> None:
        self._mesh = mesh
        self._elements = np.array(self._mesh.elements)

    def _getXY(self: 'AbstractFemModel', i: int, direction: int, element: Any) -> float:
        return element.Points[MAP_INDICES[i] - 1][direction] - element.Points[MAP_INDICES[MAP_INDICES[i]] - 1][direction]

    def _getY(self: 'AbstractFemModel', i: int, element: Any) -> float:
        return self._getXY(i, 1, element)

    def _getX(self: 'AbstractFemModel', i: int, element: Any) -> float:
        return self._getXY(i, 0, element)

    ## Specific methos for FEM
    
    def _getK(self: 'AbstractFemModel', i: int, element: Any) -> float:
        points = element.Points

        initMapIndex = MAP_INDICES[i]

        return points[initMapIndex - 1][0] * points[MAP_INDICES[initMapIndex] - 1][1] - \
            points[MAP_INDICES[initMapIndex] - 1][0] * points[initMapIndex - 1][1]

    def _getCij(self: 'AbstractFemModel', m: int, n: int, element: Any) -> Any:
        return (EPSILON_0 / (4 * element.Area)) * (self._getY(m, element) * self._getY(n, element) + self._getX(m, element) * self._getX(n, element))

    def _getLocalNodeIndexForElementGlobalIndex(self: 'AbstractFemModel', globalIndex: int, element: Any) -> int:
        return element.PointIndices.index(globalIndex)

    def _getDisjointedMatrices(self: 'AbstractFemModel') -> np.ndarray:
        C_disjointed_matrices = []

        for element in self._elements:
            C_element = np.zeros((3, 3))
            for i in range(3):
                for j in range(3):
                    C_element[i][j] = self._getCij(i + 1, j + 1, element)

            C_disjointed_matrices.append(C_element)

        return np.array(C_disjointed_matrices)

    def _createNodeToElementMap(self: 'AbstractFemModel') -> Dict[int, List[Any]]:
        pointToElementsMap: Dict[int, List[Any]] = {}
        # Loop over elements
        for element in self._elements:

            # get the 3 points of each element
            pointIndices = element.PointIndices

            # append the element to the three entries
            for pointIndex in pointIndices:
                if pointIndex not in pointToElementsMap:
                    pointToElementsMap[pointIndex] = [element]
                    continue

                # if no entry is there yet, create one
                pointToElementsMap[pointIndex].append(element)

        # TODO: Convert every list on the map to np.array
        return pointToElementsMap

    def _getVoltagesForElement(self: 'AbstractFemModel', element: Any) -> List[float]:
        return [self.nodeVoltages[pointIndex + 1] for pointIndex in element.PointIndices]

    def _getCoefficientsForElement(self: 'AbstractFemModel', element: Any, voltages: List[float]) -> List[float]:
        # area = element.Area
        # Elements area does not get an extra sign from the determinant
        area = (1/2) * sum([self._getK(i + 1, element) for i in range(3)])
        
        prefactor = 1/(2*area)
        
        a = prefactor * sum([self._getK(i + 1, element) * voltages[i] for i in range(3)])
        # Units for `b` and `c` are V/mm
        b = prefactor * sum([self._getY(i + 1, element) * voltages[i] for i in range(3)])
        c = -prefactor * sum([self._getX(i + 1, element) * voltages[i] for i in range(3)])
        
        return [a, b, c]

    def _getCoefficientDictForElements(self: 'AbstractFemModel') -> Dict[int, List[float]]:
        result = {}
        
        for element in self._elements:
            result[element.Index + 1] = self._getCoefficientsForElement(element, self._getVoltagesForElement(element))
        
        return result

    def _getVoltage(self: 'AbstractFemModel', point: List[float], linearCoefficients: List[float]):
        return linearCoefficients[0] + linearCoefficients[1] * point[0] + linearCoefficients[2] * point[1]

    def _getElectricFieldMagnitude(self: 'AbstractFemModel', linearCoefficients: List[float]) -> float:
        return math.sqrt(
            math.pow(linearCoefficients[1], 2) + math.pow(linearCoefficients[2], 2)
        )
