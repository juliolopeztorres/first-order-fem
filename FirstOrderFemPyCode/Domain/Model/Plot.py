import json
from typing import Any, List, Tuple

import matplotlib.pyplot as plt
import FirstOrderFemPyCode.Framework.Util as Util


class Plot:
    __path: str

    def __init__(self, path: str) -> None:
        self.__path = path

    def __plotColorMap(self: 'Plot', X: List[float], Y: List[float], magnitude: List[float], title: str, xlabel: str, ylabel: str) -> None:
        color_map = plt.get_cmap('Spectral')

        plt.figure(figsize=(4.8, 4.8))
        ax = plt.axes()

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        sc = ax.scatter(X, Y, c=magnitude, cmap=color_map)

        plt.colorbar(sc)
        plt.tight_layout()
        plt.show()

    def __readPlotInfoFile(self: 'Plot') -> Any:
        try:
            return json.loads(
                open(
                    Util.joinPaths(self.__path, 'plot-info.json'),
                    'r'
                ).read()
            )

        except:
            raise Exception('No plot info file was found')

    def __getValuesToPlotFromFile(self: 'Plot') -> Tuple[List[float], List[float], List[float], List[float]]:
        X, Y, Voltage, E_Magnitude = [], [], [], []

        for info in self.__readPlotInfoFile():

            X.append(info['point'][0])
            Y.append(info['point'][1])
            Voltage.append(info['voltage'])
            E_Magnitude.append(info['E_mag'])

        return X, Y, Voltage, E_Magnitude

    def writeTabSeparatedPlotInfo(self: 'Plot', x: List[float], y: List[float], voltage: List[float], eFieldMagnitude: List[float]) -> None:
        if not (len(x) == len(y) == len(voltage) == len(eFieldMagnitude)):
            raise Exception('Unexpected length for input lists. Please check!')

        try:
            with open(Util.joinPaths(self.__path, 'toPlot.dat'), 'w') as output:
                for index, xi in enumerate(x):
                    output.write(
                        f"{xi}\t{y[index]}\t{voltage[index]}\t{eFieldMagnitude[index]}\t\n")

            output.close()
        except:
            raise Exception('Error writing to parsed file')

    def run(self: 'Plot') -> None:
        X, Y, Voltage, E_Magnitude = self.__getValuesToPlotFromFile()

        self.__plotColorMap(X, Y, Voltage, "Voltage for cross section [V]", "x [mm]", "y [mm]")
        self.__plotColorMap(X, Y, E_Magnitude, "Electric field in cross section [V/mm]", "x [mm]", "y [mm]")
