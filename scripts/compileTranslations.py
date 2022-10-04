import os

from decouple import AutoConfig


def join(arg1, arg2):
    return os.path.join(arg1, arg2)


projectPath = join(os.path.dirname(__file__), '..')
config = AutoConfig(projectPath)

translationPath = os.path.join(projectPath, 'assets', 'translations')

for translation in os.listdir(translationPath):
    if not translation.endswith('.ts') or translation == 'FirstOrderFemPy.ts':
        continue

    os.popen(
        '"{}" {}'.format(
            os.path.join(config('FREECAD'), 'lrelease'),
            join(translationPath, translation)
        )
    ).read()
