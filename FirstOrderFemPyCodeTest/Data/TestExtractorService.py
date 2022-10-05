from FirstOrderFemPyCode.Data.ExtractSimulationResultsRepository import ExtractSimulationResultsRepository
from FirstOrderFemPyCode.Domain.Model.SimulationDescription import SimulationDescription
from FirstOrderFemPyCodeTest.TestAbstractSimulation import TestAbstractSimulation
from FirstOrderFemPyCode.Data.ExtractorService import ExtractorService
from FirstOrderFemPyCodeTest.MockCapacitorSimulation.capacitor import frontierElementsForCharge

class TestExtractorService(TestAbstractSimulation):
    def testExtractCenterElementsPlotInfoAndChargeForPlainPlatesCapacitor(self) -> None:
        extractor = ExtractorService(self._mesh, self._nodeVoltages)
        info = extractor.extractPlotInfo(plot=ExtractorService.Plot.ELEMENT_CENTER)
        chargeInfo = extractor.getFrontierElementsValues('1V', frontierElementsForCharge)

        self.assertEquals(4.4270938896091334e-11, sum([values['charge'] for values in chargeInfo]))
        
        # TODO: I/O could be tested separately
        repository = ExtractSimulationResultsRepository()
        simulationDescription = SimulationDescription()
        simulationDescription.mesh = self._mesh
        simulationDescription.path = TestExtractorService.PATH
        
        repository.setSimulationInformation(simulationDescription, self._nodeVoltages)
        
        repository.saveInfoToFile(info)
        repository.saveChargeInfoToFile({'1V': chargeInfo})

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
