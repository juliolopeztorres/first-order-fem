from typing import Any, Dict, List, Optional
from FirstOrderFemPyCode.Domain.Model.AbstractFemModel import AbstractFemModel
from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh

import numpy as np

class Simulation(AbstractFemModel):
    __prescribedNodes: Dict[int, float] # {18: 1.0, ..., 24: 0.0}
    __nodes: np.ndarray # List of FreeCAD Mesh.Points but ordered (prescribed at the end)

    __nodesNumber: int
    __freeNodesNumber: int

    # To be determined after `run` method
    solution: Any = None
    energy: Optional[float] = None

    def __init__(self: 'Simulation', mesh: Mesh, prescribedNodes: Dict[int, float]) -> None:
        super().__init__(mesh)
        self.__prescribedNodes = prescribedNodes

        self.__initOrderedNodes()

    def __initOrderedNodes(self: 'Simulation') -> None:
        nodes: List[Any] = self._mesh.points.copy()

        for prescribedNode, _ in self.__prescribedNodes.items():
            for node in nodes:
                if prescribedNode != node.Index + 1:
                    continue

                nodes.remove(node)
                break

            nodes.append(node)

        self.__nodes = np.array(nodes)

        self.__nodesNumber = len(self.__nodes)
        self.__freeNodesNumber = self.__nodesNumber - len(self.__prescribedNodes)

    def __getDiagonalCoefficientForJointedMatrix(self: 'Simulation', row: int, C_disjointed_matrices: np.ndarray, pointToElementsMap: Dict[int, List[Any]]) -> float:
        diagonalNode = self.__nodes[row].Index

        elementsWithGlobalNodes = pointToElementsMap[diagonalNode]

        coefficient = 0.0
        for elementWithGlobalNodes in elementsWithGlobalNodes:
            nodeLocal = self._getLocalNodeIndexForElementGlobalIndex(diagonalNode, elementWithGlobalNodes)
            coefficient += C_disjointed_matrices[elementWithGlobalNodes.Index][nodeLocal][nodeLocal]

        return coefficient

    def __getOffDiagonalCoefficientForJointedMatrix(self: 'Simulation', row: int, column: int, C_disjointed_matrices: np.ndarray, pointToElementsMap: Dict[int, List[Any]]) -> float:
        nodeGlobalIndex1, nodeGlobalIndex2 = [self.__nodes[row].Index, self.__nodes[column].Index]

        elementsWithGlobalIndex1 = pointToElementsMap[nodeGlobalIndex1]
        elementsWithGlobalIndex2 = pointToElementsMap[nodeGlobalIndex2]

        elementsWithGlobalNodes = [element for element in elementsWithGlobalIndex1 if element in elementsWithGlobalIndex2]

        coefficient = 0.0
        for elementWithGlobalNodes in elementsWithGlobalNodes:
            coefficient += C_disjointed_matrices[elementWithGlobalNodes.Index]\
                [self._getLocalNodeIndexForElementGlobalIndex(nodeGlobalIndex1, elementWithGlobalNodes)]\
                [self._getLocalNodeIndexForElementGlobalIndex(nodeGlobalIndex2, elementWithGlobalNodes)]

        return coefficient

    def __getJointedMatrix(self: 'Simulation', C_disjointed_matrices: np.ndarray, pointToElementsMap: Dict[int, List[Any]]) -> Any:
        C_jointed_matrix = np.zeros((self.__nodesNumber, self.__nodesNumber))

        for i in range(self.__nodesNumber):
            for j in range(self.__nodesNumber):
                if i == j:
                    C_jointed_matrix[i][j] = self.__getDiagonalCoefficientForJointedMatrix(i, C_disjointed_matrices, pointToElementsMap)

                    continue

                C_jointed_matrix[i][j] = self.__getOffDiagonalCoefficientForJointedMatrix(i, j, C_disjointed_matrices, pointToElementsMap)

        return C_jointed_matrix

    def __constructAndSolveLinearSystem(self: 'Simulation', C_jointed_matrix: Any) -> None:
        C_free_nodes = C_jointed_matrix[0:self.__freeNodesNumber, 0:self.__freeNodesNumber]
        C_prescribed_nodes = C_jointed_matrix[0:self.__freeNodesNumber, self.__freeNodesNumber:self.__nodesNumber]

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
                np.matmul(C_jointed_matrix[self.__freeNodesNumber:, self.__freeNodesNumber:], prescribedNodesVector)
            ))

    def solve(self: 'Simulation') -> None:
        self.__constructAndSolveLinearSystem(
            self.__getJointedMatrix(
                self._getDisjointedMatrices(),
                self._createNodeToElementMap()
            )
        )
        
        # Construct the solved node voltages dictionary
        self.nodeVoltages = {}
        for i, node in enumerate(self.__nodes[0:self.__freeNodesNumber]):
            self.nodeVoltages[node.Index + 1] = self.solution[i]

        for prescribedNodeIndex, voltaje in self.__prescribedNodes.items():
            self.nodeVoltages[prescribedNodeIndex] = voltaje
