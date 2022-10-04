from typing import Any, List, Union
from FirstOrderFemPyCode.Framework.View.TaskPanelExportOptionsPropertiesViewInterface import MatPlotLibTypeViewLabel, RenderOptionViewLabel, TaskPanelExportOptionsPropertiesViewInterface
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface
from FirstOrderFemPyCode.Framework.Service.UiLoaderServiceInterface import UiLoaderServiceInterface
from FirstOrderFemPyCode.Framework.Command.ExportOptions.ViewObject import ViewObject

class TaskPanelExportOptionsPropertiesView(TaskPanelExportOptionsPropertiesViewInterface):
    __callback: TaskPanelExportOptionsPropertiesViewInterface.Callback
    form: Any

    def __init__(
        self,
        uiLoaderService: UiLoaderServiceInterface,
        callback: TaskPanelExportOptionsPropertiesViewInterface.Callback,
        obj: ViewObject.ExportOptionsDataContainer,
        childs: List[ViewInterface] = None
    ):
        self.form = uiLoaderService.load("TaskPanelExportOptionsProperties")
        self.__callback = callback
        
        self.form.inputRenderOption.addItems([renderOption.value for renderOption in RenderOptionViewLabel])
        self.form.inputPlotLibType.addItems([matPlotLibType.value for matPlotLibType in MatPlotLibTypeViewLabel])
        
        self.__initInputEvents()

    def __initInputEvents(self: 'TaskPanelExportOptionsPropertiesView') -> None:
        self.form.inputRenderOption.currentIndexChanged.connect(
            lambda selectedIndex: self.__onInputChanged(
                'renderOption',
                list(RenderOptionViewLabel)[selectedIndex]
            )
        )

        self.form.inputPlotLibType.currentIndexChanged.connect(
            lambda selectedIndex: self.__onInputChanged(
                'matPlotLibType',
                list(MatPlotLibTypeViewLabel)[selectedIndex]
            )
        )

        self.form.inputPointsPerDirection.textChanged.connect(
            lambda text: self.__onInputChanged('pointsPerDirection', int(text))
        )

    def __onInputChanged(self: 'TaskPanelExportOptionsPropertiesView', input: str, value: Union[RenderOptionViewLabel, MatPlotLibTypeViewLabel, int]) -> None:
        self.__callback.onInputChanged(
            input, 
            value
        )

        self.__updateUi()

    def __updateUi(self: 'TaskPanelExportOptionsPropertiesView') -> None:
        self.form.plotLibSection.setVisible(
            list(RenderOptionViewLabel)[self.form.inputRenderOption.currentIndex()] == RenderOptionViewLabel.MATPLOTLIB
        )
        
        self.form.pointsPerDirectionSection.setVisible(
            list(MatPlotLibTypeViewLabel)[self.form.inputPlotLibType.currentIndex()]== MatPlotLibTypeViewLabel.CARTESIAN
        )

    def accept(self: 'TaskPanelExportOptionsPropertiesView') -> None:
        self.__callback.onAccept()

    def reject(self: 'TaskPanelExportOptionsPropertiesView') -> None:
        self.__callback.onReject()

    def closing(self: 'TaskPanelExportOptionsPropertiesView') -> None:
        self.__callback.onClose()

    def loadData(self: 'TaskPanelExportOptionsPropertiesView', optionsModel: TaskPanelExportOptionsPropertiesViewInterface.OptionsModel) -> None:
        self.form.inputRenderOption.setCurrentIndex(list(RenderOptionViewLabel).index(optionsModel.renderOption))
        self.form.inputPlotLibType.setCurrentIndex(list(MatPlotLibTypeViewLabel).index(optionsModel.matPlotLibType))
        self.form.inputPointsPerDirection.setText(str(optionsModel.pointsPerDirection))
        
        self.__updateUi()

    def getActualView(self) -> Any:
        return self.form
