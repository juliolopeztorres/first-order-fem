from abc import ABC
from typing import Any, Dict
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
