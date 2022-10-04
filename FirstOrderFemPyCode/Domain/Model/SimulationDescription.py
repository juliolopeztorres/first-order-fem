from typing import Dict, List, NewType
from FirstOrderFemPyCode.Domain.Model.ExportOptions import ExportOptions

from FirstOrderFemPyCode.Domain.Model.Mesh import Mesh

PrescribedNodesType = NewType('PrescribedNodesType', Dict[int, float])
FrontierElementsType = NewType('FrontierElementsType', List[int])
FrontierElementsGroupsType = NewType('FrontierElementsGroupsType', Dict[str, FrontierElementsType])

class SimulationDescription:
    path: str
    
    mesh: Mesh
    prescribedNodes: PrescribedNodesType
    frontierElementsGroups: FrontierElementsGroupsType
    exportOptions: ExportOptions
