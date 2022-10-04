from typing import Any, List

from FirstOrderFemPyCode.Domain.Model.SimulationDescription import PrescribedNodesType, SimulationDescription, FrontierElementsType, FrontierElementsGroupsType
from FirstOrderFemPyCode.Framework.Mapper.ExportOptionsMapper import ExportOptionsMapper
from FirstOrderFemPyCode.Framework.Mapper.MeshMapper import MeshMapper
import FirstOrderFemPyCode.Framework.Util as Util
from FirstOrderFemPyCode.Framework.Command.MeshContainer.ViewProvider import ViewProvider as MeshContainerViewProvider
from FirstOrderFemPyCode.Framework.Command.PrescribedNodesContainer.ViewProvider import ViewProvider as PrescribedNodesContainerViewProvider
from FirstOrderFemPyCode.Framework.Command.FrontierElementsContainer.ViewProvider import ViewProvider as FrontierElementsContainerViewProvider
from FirstOrderFemPyCode.Framework.Command.ExportOptions.ViewProvider import ViewProvider as ExportOptionsViewProvider
from FirstOrderFemPyCode.Framework.Command.PrescribedNodeGroup.ViewObject import ViewObject as PrescribedNodeGroupViewObject
from FirstOrderFemPyCode.Framework.Command.FrontierElementGroup.ViewObject import ViewObject as FrontierElementGroupViewObject
from FirstOrderFemPyCode.Framework.Command.SimulationContainer.ViewObject import ViewObject as SimulationContainerViewObject

class SimulationDescriptionMapper:
    
    @staticmethod
    def map(freeCADSimulationContainer: SimulationContainerViewObject.SimulationContainerDataContainer, path: str) -> SimulationDescription:
        simulationDescription = SimulationDescription()

        simulationDescription.path = path

        meshContainerFreeCAD = Util.getDataObjectsWithViewObjectProxyInstance(
            freeCADSimulationContainer.Group,
            MeshContainerViewProvider
        )[0]

        simulationDescription.mesh = MeshMapper.map(meshContainerFreeCAD)

        prescribedNodesContainerFreeCAD = Util.getDataObjectsWithViewObjectProxyInstance(
            freeCADSimulationContainer.Group,
            PrescribedNodesContainerViewProvider
        )[0]

        simulationDescription.prescribedNodes = SimulationDescriptionMapper.mapPrescribedNodes(prescribedNodesContainerFreeCAD)
        
        frontierElementsContainerFreeCAD = Util.getDataObjectsWithViewObjectProxyInstance(
            freeCADSimulationContainer.Group,
            FrontierElementsContainerViewProvider
        )[0]

        simulationDescription.frontierElementsGroups = SimulationDescriptionMapper.mapFrontierElementsGroups(frontierElementsContainerFreeCAD)

        exportOptionsFreeCAD = Util.getDataObjectsWithViewObjectProxyInstance(
            freeCADSimulationContainer.Group,
            ExportOptionsViewProvider
        )[0]

        simulationDescription.exportOptions = ExportOptionsMapper.map(exportOptionsFreeCAD)
        
        return simulationDescription

    @staticmethod
    def mapPrescribedNodes(prescribedNodesContainerFreeCAD: Any) -> PrescribedNodesType:
        voltageGroups: List[PrescribedNodeGroupViewObject.PrescribedNodeGroupDataContainer] = prescribedNodesContainerFreeCAD.Group
        
        prescribedNodes: PrescribedNodesType = {} # type: ignore
        
        for voltageItem in voltageGroups:
            for node in voltageItem.Group:
                prescribedNodes[int(node.Label)] = float(voltageItem.Voltage)
        
        return prescribedNodes
    
    @staticmethod
    def mapFrontierElementsGroups(frontierElementsContainerFreeCAD: Any) -> FrontierElementsGroupsType:
        frontierElementsGroups: FrontierElementsGroupsType = {} # type: ignore
        
        frontierGroups: List[FrontierElementGroupViewObject.FrontierElementGroupDataContainer] = frontierElementsContainerFreeCAD.Group
        
        for frontierGroup in frontierGroups:
            frontierElementsGroups[frontierGroup.Label.replace(' ', '_')] = FrontierElementsType([int(element.Label) for element in frontierGroup.Group])
        
        return frontierElementsGroups
