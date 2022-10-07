from FirstOrderFemPyCode.Data.VtkService import VtkService
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import \
    SimulationDescription
from FirstOrderFemPyCodeTest.TestAbstractSimulation import \
    TestAbstractSimulation


class TestVtkService(TestAbstractSimulation):
    def testExtractVtkPlotInfoForPlainPlatesCapacitor(self) -> None:
        simulationDescription = SimulationDescription()
        simulationDescription.path = TestVtkService.PATH
        simulationDescription.mesh = self._mesh
        
        VtkService(simulationDescription).export(
            self._nodeVoltages,
            self._readFile(self._getTestFilePath('capacitor-plot-info-vtk.json'), 'Could not retrieve Vtk plot file'),  # type: ignore
            open=False
        )

        try:
            contents = open(self._getOutputFilePath(
                "paraview-info.vtu"), 'rb').read()
            expectedContents = open(self._getTestFilePath(
                'capacitor-paraview-info.vtu'), 'rb').read()
        except Exception:
            self.fail(
                'Could not retrieve either output or expected Paraview file')

        self.assertEqual(expectedContents, contents)
