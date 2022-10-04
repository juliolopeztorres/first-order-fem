from FirstOrderFemPyCodeTest.TestAbstractSimulation import TestAbstractSimulation
from FirstOrderFemPyCode.Domain.Model.Extractor import Extractor
from FirstOrderFemPyCodeTest.MockCapacitorSimulation.capacitor import frontierElementsForCharge

# TODO: Check Framework layer usage
import FirstOrderFemPyCode.Framework.Util as Util

class TestExtractor(TestAbstractSimulation):
    def testExtractCenterElementsPlotInfoAndChargeForPlainPlatesCapacitor(self) -> None:
        extractor = Extractor(TestExtractor.PATH, self._mesh, self._nodeVoltages)
        extractor.extractPlotInfo(plot=Extractor.Plot.ELEMENT_CENTER)

        self.assertEquals(
            4.4270938896091334e-11, 
            extractor.extractChargeOnFrontier('1V', frontierElementsForCharge)
        )
        
        pairs = [
            (
                {'filename': 'plot-info.json', 'exceptionMessage': "Could not retrieve plot-info file"}, 
                {'filename': 'capacitor-plot-info.json', 'exceptionMessage': "Could not retrieve expected plot-info file"}, 
            ),
            (
                {'filename': 'relevant-electric-field-vector_1V.json', 'exceptionMessage': "Could not retrieve electric-field-vector file"}, 
                {'filename': 'capacitor-charge-info.json', 'exceptionMessage': "Could not retrieve expected charge-info file"}, 
            ),
        ]

        for pair in pairs:
            self.assertEquals(
                self._readFile(
                    self._getOutputFilePath(pair[0]['filename']),
                    pair[0]['exceptionMessage']
                ), 
                self._readFile(
                    self._getTestFilePath(pair[1]['filename']),
                    pair[1]['exceptionMessage']
                )
            )
