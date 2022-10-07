from decouple import AutoConfig
import FirstOrderFemPyCode.Framework.Util as Util
config = AutoConfig(Util.getModulePath())

if config('APP_ENV') == 'dev':
    import ptvsd

    ptvsd.enable_attach(address=('localhost', 5678))
    # ptvsd.wait_for_attach()

from enum import Enum, auto, unique
from typing import Any, Callable, Dict, List, Optional

# Services and use cases
from FirstOrderFemPyCode.Framework.Service.UiLoaderService import UiLoaderService
from FirstOrderFemPyCode.Framework.Service.UiLoaderServiceInterface import UiLoaderServiceInterface
from FirstOrderFemPyCode.Data.DataRepository import DataRepository
from FirstOrderFemPyCode.Domain.ExtractSimulationResultsUseCase.ExtractSimulationResultsUseCase import ExtractSimulationResultsUseCase
from FirstOrderFemPyCode.Domain.RunSimulationUseCase.RunSimulationUseCase import RunSimulationUseCase

# Views
from FirstOrderFemPyCode.Framework.View.TaskPanelPrescribedNodeGroupPropertiesView import TaskPanelPrescribedNodeGroupPropertiesView
from FirstOrderFemPyCode.Framework.View.TaskPanelExportOptionsPropertiesView import TaskPanelExportOptionsPropertiesView
from FirstOrderFemPyCode.Framework.View.TaskPanelSimulationContainerPropertiesView import TaskPanelSimulationContainerPropertiesView
from FirstOrderFemPyCode.Framework.View.ProgressBarView import ProgressBarView
from FirstOrderFemPyCode.Framework.View.ViewInterface import ViewInterface

# Initialization of services and use cases
dataRepository = DataRepository()

@unique
class Service(Enum):
    UI_LOADER_SERVICE = auto()
    DATA_REPOSITORY = auto()
    RUN_SIMULATION_USE_CASE = auto()
    EXTRACT_SIMULATION_RESULTS_USE_CASE = auto()


dictionaryServices = {
    Service.UI_LOADER_SERVICE: UiLoaderService(),
    Service.DATA_REPOSITORY: dataRepository,
    Service.EXTRACT_SIMULATION_RESULTS_USE_CASE: ExtractSimulationResultsUseCase(dataRepository),
    Service.RUN_SIMULATION_USE_CASE: RunSimulationUseCase(dataRepository),
}


@unique
class View(Enum):
    TASK_PANEL_PRESCRIBED_NODE_GROUP_PROPERTIES_VIEW = auto()
    TASK_PANEL_EXPORT_OPTIONS_PROPERTIES_VIEW = auto()
    TASK_PANEL_SIMULATION_CONTAINER_PROPERTIES_VIEW = auto()

    PROGRESS_BAR_VIEW = auto()


# Fist Any -> ViewInterface.Callback or children, Second Any -> Data Object (Optional), Third Any -> List of childs (Optional)
CreateViewCallableType = Callable[
    [UiLoaderServiceInterface, Any, Optional[Any], Optional[List[Any]]],
    ViewInterface
]
# Any -> Valid ViewInterface or children
CreateCallable: Callable[[Any], CreateViewCallableType] = \
    lambda Class: \
    lambda uiLoaderService, callback, dataObject, childs: Class(
        uiLoaderService,
        callback,
        dataObject,
        childs
)

dictionaryViews: Dict[View, CreateViewCallableType] = {
    View.TASK_PANEL_PRESCRIBED_NODE_GROUP_PROPERTIES_VIEW: CreateCallable(TaskPanelPrescribedNodeGroupPropertiesView),
    View.TASK_PANEL_EXPORT_OPTIONS_PROPERTIES_VIEW: CreateCallable(TaskPanelExportOptionsPropertiesView),
    View.TASK_PANEL_SIMULATION_CONTAINER_PROPERTIES_VIEW: CreateCallable(TaskPanelSimulationContainerPropertiesView),
    
    View.PROGRESS_BAR_VIEW: CreateCallable(ProgressBarView),
}


class Container:
    @staticmethod
    def getService(service: Service) -> Any:
        if service not in dictionaryServices:
            raise Exception('Service not found')

        return dictionaryServices.get(service)

    @staticmethod
    def getView(
        view: View,
        callback: ViewInterface.CallbackInterface,
        dataObject: Optional[Any] = None,
        childs: Optional[List[View]] = None
    ) -> Any:
        if view not in dictionaryViews:
            raise Exception('View not found')

        Callable = dictionaryViews.get(view)

        if not Callable:
            raise Exception('Could not retrieve callable')

        createdChilds = None
        if childs and len(childs) > 0:
            createdChilds = Container.__getChildViews(
                childs,
                callback,
                dataObject
            )

        return Callable(
            Container.getService(Service.UI_LOADER_SERVICE),
            callback,
            dataObject,
            createdChilds
        )

    @staticmethod
    def __getChildViews(
        childs: List[View],
        callback: ViewInterface.CallbackInterface,
        dataObject: Optional[Any] = None
    ) -> List[Any]:
        createdChilds = []
        for child in childs:
            ChildCallable = dictionaryViews.get(child)

            if not ChildCallable:
                raise Exception(
                    'Bad Child specification. Could not retrieve callable'
                )

            createdChilds.append(
                ChildCallable(
                    Container.getService(Service.UI_LOADER_SERVICE),
                    callback,
                    dataObject,
                    None  # Only supporting 1 View -> embedding n "Not embedding others"-views
                )
            )

        return createdChilds
