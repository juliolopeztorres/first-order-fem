from FirstOrderFemPyCode.Framework.Command.ExportOptions.DataContainer import DataContainer
from FirstOrderFemPyCode.Framework.Command.Interface import ViewObjectInterface


class ViewObject(ViewObjectInterface):
    class ExportOptionsDataContainer(ViewObjectInterface.ObjectInterface):
        Proxy: DataContainer
        
        RenderOption: str # RenderOption value
        MatPlotLibType: str # MatPlotLibType value
        PointsPerDirection: int

    Object: ExportOptionsDataContainer
