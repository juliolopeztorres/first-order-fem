import FirstOrderFemPyCodeTest as Suite
from unittest import TestLoader, TextTestRunner

# ---- DEVELOPMENT | When reloading in FreeCAD UI
#
# from importlib import reload

# from FirstOrderFemPyCode.Framework.View import MyView
# reload(MyView)

# reload(Suite)
#
# ------------------------------------------------

TextTestRunner().run(
    TestLoader().loadTestsFromModule(Suite)
)
