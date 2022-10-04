from typing import Dict, Optional
from FirstOrderFemPyCode.Domain.Model.ExportOptions import MatPlotLibType, RenderOption
from FirstOrderFemPyCode.Domain.Model.ExportVtk import ExportVtk
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription
from FirstOrderFemPyCode.Domain.Model.Extractor import Extractor
from FirstOrderFemPyCode.Domain.Model.Plot import Plot

class ExtractSimulationResultsUseCase:
    def extract(self: 'ExtractSimulationResultsUseCase', simulationDescription: SimulationDescription, nodeVoltages: Optional[Dict[int, float]]) -> None:
        extractor = Extractor(simulationDescription.path, simulationDescription.mesh, nodeVoltages)
        
        if simulationDescription.exportOptions.renderOption == RenderOption.VTK:
            EVectorInfo = extractor.extractPlotInfo(Extractor.Plot.VTK)
            
            ExportVtk(simulationDescription.path).run(simulationDescription.mesh, nodeVoltages, EVectorInfo)
        else:
            if simulationDescription.exportOptions.matPlotLibType == MatPlotLibType.MIDDLE_POINTS:    
                extractor.extractPlotInfo(Extractor.Plot.ELEMENT_CENTER)
            else:
                extractor.extractPlotInfo(Extractor.Plot.CARTESIAN_GRID, simulationDescription.exportOptions.pointsPerDirection)
            
            Plot(simulationDescription.path).run()

        for frontierElementsGroupName, elements in simulationDescription.frontierElementsGroups.items():
            print(f'Total charge on frontier {frontierElementsGroupName}: {extractor.extractChargeOnFrontier(frontierElementsGroupName, elements)}C\n')
