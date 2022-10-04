# First Order Finite Elements Method Python

User interface layer written in Python to help __FreeCAD__ understand a sample workflow to resolve Finite Element problems in first order.

## Dependencies

At the moment, you would need to configure _FreeCAD_ to load 3rd party libraries from within its configuration. Dependencies used in the app are:

- `FreeCAD`         |   0.19 | 3D View and base design line using Qt. Usage of `lupdate` and `lconvert` for translation
- `python-decouple` |    3.5 | Loading `env` variables
- `PyQt5`           | 5.15.6 | Usage of `pylupdate` for translation
- `numpy`           | 1.19.3 | Plotting helper utilities
- `ptvsd`           |  4.3.2 | FreeCAD debugging on VS Code (Windows)

Install dependencies by `pip install -r requirements.txt` or install to a local folder by using `pip install -r requirements.txt -t lib_modules`.

## Build
There is no need to perform any particular action to run this code. You would only need to copy the folder to your __FreeCAD__\Mod path and restart the program. Currently, it has been tested under Windows 10. The path for it to work would be something like `%appdata%\freecad\mod`
