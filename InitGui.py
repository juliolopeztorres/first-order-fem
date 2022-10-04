import FreeCADGui

import FirstOrderFemPyCode.Framework.Container

class FirstOrderFemPy(FreeCADGui.Workbench):
    def __init__(self):
        import os

        from FreeCAD import Qt
        import FirstOrderFemPyCode.Framework.Util as Util

        FreeCADGui.addLanguagePath(os.path.join(Util.getModulePath(), "assets", "translations"))
        FreeCADGui.updateLocale()

        self.__class__.Icon = os.path.join(Util.getModulePath(), 'assets', 'icons', 'logo.svg')
        self.__class__.MenuText = "1º Order FEM"
        self.__class__.ToolTip = "First Order FEM Python"

        from PySide import QtCore

        ICONS_PATH = os.path.join(Util.getModulePath(), "assets", "icons")
        QtCore.QDir.addSearchPath("icons", ICONS_PATH)

        # PreferencesView cannot be retrieved from the Container as FreeCAD is the one creating the instance
        # from FirstOrderFemPyCode.Framework.View.PreferencesView import PreferencesView
        # FreeCADGui.addPreferencePage(PreferencesView, Qt.translate("FirstOrderFemPyInit", "PREFERENCE"))

    def Initialize(self):
        # must import QtCore in this function,
        # not at the beginning of this file for translation support
        from FreeCAD import Qt

        self.registerCommands()

        cmdlst = [
            'SimulationContainer',
            'Separator',
            'MeshContainer',
            'Separator',
            'PrescribedNodesContainer',
            'PrescribedNodeGroup',
            'Separator',
            'FrontierElementsContainer',
            'FrontierElementGroup',
            'Separator',
            'ExportOptions',
        ]

        self.appendMenu(Qt.translate("FirstOrderFemPyInit", "MENU"), cmdlst)

        cmdlst.extend(['Separator', 'LoadElementsAndNodes'])

        self.appendToolbar(Qt.translate("FirstOrderFemPyInit", "TOOLBAR"), cmdlst)

        # For some reason, FreeCAD cannot see the import at the top of the file
        from FirstOrderFemPyCode.Framework.Container import Container, Service

        self.contextMenuText = Qt.translate("FirstOrderFemPyInit", "MENU")

    def registerCommands(self):
        from FirstOrderFemPyCode.Framework.Command.ExportOptions.Command import Command as ExportOptions
        from FirstOrderFemPyCode.Framework.Command.FrontierElementGroup.Command import Command as FrontierElementGroup
        from FirstOrderFemPyCode.Framework.Command.FrontierElementsContainer.Command import Command as FrontierElementsContainer
        from FirstOrderFemPyCode.Framework.Command.LoadElementsAndNodes.Command import Command as LoadElementsAndNodes
        from FirstOrderFemPyCode.Framework.Command.MeshContainer.Command import Command as MeshContainer
        from FirstOrderFemPyCode.Framework.Command.PrescribedNodeGroup.Command import Command as PrescribedNodeGroup
        from FirstOrderFemPyCode.Framework.Command.PrescribedNodesContainer.Command import Command as PrescribedNodesContainer
        from FirstOrderFemPyCode.Framework.Command.SimulationContainer.Command import Command as SimulationContainer
        
        FreeCADGui.addCommand('ExportOptions', ExportOptions())
        FreeCADGui.addCommand('FrontierElementGroup', FrontierElementGroup())
        FreeCADGui.addCommand('FrontierElementsContainer', FrontierElementsContainer())
        FreeCADGui.addCommand('LoadElementsAndNodes', LoadElementsAndNodes())
        FreeCADGui.addCommand('MeshContainer', MeshContainer())
        FreeCADGui.addCommand('PrescribedNodeGroup', PrescribedNodeGroup())
        FreeCADGui.addCommand('PrescribedNodesContainer', PrescribedNodesContainer())
        FreeCADGui.addCommand('SimulationContainer', SimulationContainer())

    def ContextMenu(self, recipient):
        # self.appendContextMenu(self.contextMenuText, ['MyOtherCommandMore'])
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Activated(self):
        FreeCADGui.updateLocale()

    def Deactivated(self):
        pass

FreeCADGui.addWorkbench(FirstOrderFemPy())
