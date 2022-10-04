from FirstOrderFemPyCode.Domain.Model.ExportVtk import ExportVtk
from FirstOrderFemPyCodeTest.TestAbstractSimulation import TestAbstractSimulation


class TestExportVtk(TestAbstractSimulation):
    def testExtractVtkPlotInfoForPlainPlatesCapacitor(self) -> None:
        ExportVtk(TestExportVtk.PATH).run(
            self._mesh,
            self._nodeVoltages,
            self._readFile(self._getTestFilePath(
                'capacitor-plot-info-vtk.json'), 'Could not retrieve Vtk plot file'),  # type: ignore
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
