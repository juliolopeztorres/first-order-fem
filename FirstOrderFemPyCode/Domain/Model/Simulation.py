# import json
from typing import Any, Dict, List, Optional
from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh

import numpy as np
from FirstOrderFemPyCode.Domain.Model import EPSILON_0, MAP_INDICES

class Simulation:
    __mesh: Mesh
    __prescribedNodes: Dict[int, float] # {18: 1.0, ..., 24: 0.0}
    __elements: np.ndarray # List of FreeCAD Mesh.Facets
    __nodes: np.ndarray # List of FreeCAD Mesh.Points but ordered (prescribed at the end)

    __nodesNumber: int
    __freeNodesNumber: int

    # To be determined after `run` method
    solution: Any = None
    energy: Optional[float] = None
    nodeVoltages: Optional[Dict[int, float]] = None

    def __init__(self: 'Simulation', mesh: Mesh, prescribedNodes: Dict[int, float]) -> None:
        self.__mesh = mesh
        self.__elements = np.array(self.__mesh.elements)
        self.__prescribedNodes = prescribedNodes

        self.__initOrderedNodes()

    def __initOrderedNodes(self: 'Simulation') -> None:
        nodes: List[Any] = self.__mesh.points.copy()

        for prescribedNode, _ in self.__prescribedNodes.items():
            for node in nodes:
                if prescribedNode != node.Index + 1:
                    continue

                nodes.remove(node)
                break

            nodes.append(node)

        self.__nodes = np.array(nodes)

        self.__nodesNumber = len(self.__nodes)
        self.__freeNodesNumber = self.__nodesNumber - \
            len(self.__prescribedNodes)

    def __getXY(self: 'Simulation', i: int, direction: int, element: Any) -> float:
        return element.Points[MAP_INDICES[i] - 1][direction] - element.Points[MAP_INDICES[MAP_INDICES[i]] - 1][direction]

    def __getY(self: 'Simulation', i: int, element: Any) -> float:
        return self.__getXY(i, 1, element)

    def __getX(self: 'Simulation', i: int, element: Any) -> float:
        return self.__getXY(i, 0, element)

    def __getCij(self: 'Simulation', m: int, n: int, element: Any) -> Any:
        return (EPSILON_0 / (4 * element.Area)) * (self.__getY(m, element) * self.__getY(n, element) + self.__getX(m, element) * self.__getX(n, element))

    def __getLocalNodeIndexForElementGlobalIndex(self: 'Simulation', globalIndex: int, element: Any) -> int:
        return element.PointIndices.index(globalIndex)

    def __getDisjointedMatrices(self: 'Simulation') -> np.ndarray:
        C_disjoin_matrices = []

        for element in self.__elements:
            C_element = np.zeros((3, 3))
            for i in range(3):
                for j in range(3):
                    C_element[i][j] = self.__getCij(i + 1, j + 1, element)

            C_disjoin_matrices.append(C_element)

        return np.array(C_disjoin_matrices)

    def __createNodeToElementMap(self: 'Simulation') -> Dict[int, List[Any]]:
        pointToElementsMap: Dict[int, List[Any]] = {}
        # Loop over elements
        for element in self.__elements:

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

    def __getJointedMatrix(self: 'Simulation', C_disjoin_matrices: np.ndarray, pointToElementsMap: Dict[int, List[Any]]) -> Any:
        C_join_matrix = np.zeros((self.__nodesNumber, self.__nodesNumber))

        for i in range(self.__nodesNumber):
            for j in range(self.__nodesNumber):
                if i == j:
                    # Diagonal
                    diagonalNode = self.__nodes[i].Index

                    elementsWithGlobalNodes = pointToElementsMap[diagonalNode]

                    coefficient = 0.0
                    for elementWithGlobalNodes in elementsWithGlobalNodes:
                        nodeLocal = self.__getLocalNodeIndexForElementGlobalIndex(diagonalNode, elementWithGlobalNodes)
                        coefficient += C_disjoin_matrices[elementWithGlobalNodes.Index][nodeLocal][nodeLocal]

                    C_join_matrix[i][j] = coefficient

                    continue

                # Off diagonal
                nodeGlobalIndex1, nodeGlobalIndex2 = [self.__nodes[i].Index, self.__nodes[j].Index]

                elementsWithGlobalIndex1 = pointToElementsMap[nodeGlobalIndex1]
                elementsWithGlobalIndex2 = pointToElementsMap[nodeGlobalIndex2]

                elementsWithGlobalNodes = [element for element in elementsWithGlobalIndex1 if element in elementsWithGlobalIndex2]

                coefficient = 0.0
                for elementWithGlobalNodes in elementsWithGlobalNodes:
                    coefficient += C_disjoin_matrices[elementWithGlobalNodes.Index]\
                        [self.__getLocalNodeIndexForElementGlobalIndex(nodeGlobalIndex1, elementWithGlobalNodes)]\
                        [self.__getLocalNodeIndexForElementGlobalIndex(nodeGlobalIndex2, elementWithGlobalNodes)]

                C_join_matrix[i][j] = coefficient

        return C_join_matrix

    def __constructAndSolveLinearSystem(self: 'Simulation', C_join_matrix: Any) -> None:
        C_free_nodes = C_join_matrix[0:self.__freeNodesNumber, 0:self.__freeNodesNumber]
        C_prescribed_nodes = C_join_matrix[0:self.__freeNodesNumber, self.__freeNodesNumber:self.__nodesNumber]

        prescribedNodesVector = np.array(list(self.__prescribedNodes.values()))
        independantCoeficient = np.matmul(C_prescribed_nodes, prescribedNodesVector)

        self.solution = np.linalg.solve(C_free_nodes, -independantCoeficient)

        # Total elements energy in J
        self.energy = (1/2) * (
            np.matmul(self.solution.transpose(), np.matmul(C_free_nodes, self.solution)) +
            np.matmul(self.solution.transpose(), np.matmul(C_prescribed_nodes, prescribedNodesVector)) +
            np.matmul(prescribedNodesVector.transpose(), np.matmul(C_prescribed_nodes.transpose(), self.solution)) +
            np.matmul(
                prescribedNodesVector.transpose(), 
                np.matmul(C_join_matrix[self.__freeNodesNumber:, self.__freeNodesNumber:], prescribedNodesVector)
            ))

    def run(self: 'Simulation') -> None:
        self.__constructAndSolveLinearSystem(
            self.__getJointedMatrix(
                self.__getDisjointedMatrices(),
                self.__createNodeToElementMap()
            )
        )
        
        # Construct the solved node voltages dictionary
        self.nodeVoltages = {}
        for i, node in enumerate(self.__nodes[0:self.__freeNodesNumber]):
            self.nodeVoltages[node.Index + 1] = self.solution[i]

        for prescribedNodeIndex, voltaje in self.__prescribedNodes.items():
            self.nodeVoltages[prescribedNodeIndex] = voltaje
