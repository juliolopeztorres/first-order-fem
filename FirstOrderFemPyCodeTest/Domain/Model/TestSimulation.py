from FirstOrderFemPyCode.Data.DataRepository import DataRepository
from FirstOrderFemPyCode.Domain.Model.Simulation import Simulation
from FirstOrderFemPyCodeTest.TestAbstractSimulation import TestAbstractSimulation
from FirstOrderFemPyCodeTest.MockCapacitorSimulation.capacitor import prescribedNodes

class TestSimulation(TestAbstractSimulation):
    def testPlainPlatesCapacitor(self) -> None:       
        simulation = Simulation(self._mesh, prescribedNodes)#, TestSimulation.PATH)
        
        simulation.run()
               
        self.assertEquals(2.2135469609968867e-11, simulation.energy)
        self.assertListEqual(
            [
                0.6818906595771825,
                0.6485965267433162,
                0.5070684488953491,
                0.4965277962908612,
                0.49565971169735695,
                0.4897073512601469,
                0.48958334926257807,
                0.4895833434440906,
                0.48784721055908864,
                0.486111112186414,
                0.3512356197553776,
                0.31045616815647503
            ],
            list(simulation.solution)
        )
        
        # TODO: I/O could be tested separately
        if not simulation.nodeVoltages:
            self.fail('Could not retrieve solution node voltages')    
            
        DataRepository().writeNodeVoltages(TestSimulation.PATH, 'solution.json', simulation.nodeVoltages)

        self.assertEquals(
            self._readFile(
                self._getOutputFilePath('solution.json'),
                "Could not retrieve solution file"
            ), 
            self._readFile(
                self._getTestFilePath('capacitor-solution.json'),
                "Could not retrieve expected solution file"
            )
        )
