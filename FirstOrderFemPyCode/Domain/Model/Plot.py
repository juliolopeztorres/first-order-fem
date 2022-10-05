from typing import Any, List, Tuple

import matplotlib.pyplot as plt


class Plot:
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

    def __mapValuesToPlotFromInfo(self: 'Plot', plotInfo: List[Any]) -> Tuple[List[float], List[float], List[float], List[float]]:
        X, Y, Voltage, E_Magnitude = [], [], [], []

        for info in plotInfo:
            X.append(info['point'][0])
            Y.append(info['point'][1])
            Voltage.append(info['voltage'])
            E_Magnitude.append(info['E_mag'])

        return X, Y, Voltage, E_Magnitude

    def run(self: 'Plot', plotInfo: List[Any]) -> None:
        X, Y, Voltage, E_Magnitude = self.__mapValuesToPlotFromInfo(plotInfo)

        self.__plotColorMap(X, Y, Voltage, "Voltage for cross section [V]", "x [mm]", "y [mm]")
        self.__plotColorMap(X, Y, E_Magnitude, "Electric field in cross section [V/mm]", "x [mm]", "y [mm]")
