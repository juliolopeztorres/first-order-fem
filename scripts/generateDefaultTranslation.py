import os
import subprocess
import re
from typing import List

import numpy
from decouple import AutoConfig

# `pylupdate5` and `windows` have limitations on command line arguments
DIVISIONS = 20


def join(arg1, arg2):
    return os.path.join(arg1, arg2)


def getAllPythonFiles(fileOrFolder, sourcePath, list):
    if fileOrFolder == '__pycache__':
        return

    fullFileFolderPath = join(sourcePath, fileOrFolder)

    if os.path.isfile(fullFileFolderPath) and fileOrFolder.endswith('.py'):
        list.append(fullFileFolderPath)
        return

    if os.path.isdir(fullFileFolderPath):
        subFilesOrFolders = os.listdir(fullFileFolderPath)

        for subFileOrFolder in subFilesOrFolders:
            getAllPythonFiles(
                subFileOrFolder,
                fullFileFolderPath,
                list
            )


def removeLinesAttr(translationNamePath):
    regexp = re.compile('(line="\d*")\s?')

    pythonFilesContent = open(translationNamePath, "r")
    lines = pythonFilesContent.readlines()
    pythonFilesContent.close()

    pythonFilesContent = open(translationNamePath, "w")
    for line in lines:
        result = regexp.search(line)
        if result is not None:
            span = result.span()
            line = line[:span[0]] + line[span[1]:]

        pythonFilesContent.write(line)

    pythonFilesContent.close()


def removeUnfinishedTranslations(translationNamePath):
    pythonFilesContent = open(translationNamePath, "r")
    lines = pythonFilesContent.readlines()
    pythonFilesContent.close()

    pythonFilesContent = open(translationNamePath, "w")
    for line in lines:
        if '<translation type="unfinished"></translation>' in line:
            continue

        pythonFilesContent.write(line)

    pythonFilesContent.close()


def splitAndProcessPythonFiles(allPythonFiles, outputPythonFile):
    pythonTranslationFilenamePathFormat = join(
        translationPath, 'tempPythonFiles{number}.ts'
    )

    parts = [part for part in numpy.array_split(
        allPythonFiles, DIVISIONS) if len(part) > 0]

    i = 1
    temporaryNames = []
    for part in parts:
        temporaryName = pythonTranslationFilenamePathFormat.format(
            number='-{}'.format(i)
        )

        tempResult = subprocess.run(
            'pylupdate5 {} -ts {} -verbose'.format(
                ' '.join(part),
                temporaryName
            ),
            capture_output=True,
            text=True
        ).stderr

        result = re.findall('Found (\d+) source texts', tempResult)

        if len(result) == 1 and int(result[0]) > 0:
            temporaryNames.append(temporaryName)
            i += 1
        else:
            os.remove(temporaryName)

    # Join split parts into one single to be joined later with the `ts` coming from `.ui`
    os.popen(
        '"{}" -i {} -o {} -no-ui-lines'.format(
            os.path.join(config('FREECAD'), 'lconvert'),
            ' '.join(temporaryNames),
            outputPythonFile
        )
    ).read()

    removeLinesAttr(outputPythonFile)

    for temporaryName in temporaryNames:
        os.remove(temporaryName)


os.chdir(os.path.dirname(__file__))

projectPath = join('.', '..')
config = AutoConfig(projectPath)

translationPath = os.path.join(projectPath, 'assets', 'translations')
uiPath = os.path.join(projectPath, 'assets', 'ui')

uiTranslationFilename = 'uiFiles.ts'
pythonTranslationFilename = 'pythonFiles.ts'
defaultTranslationFilename = 'FirstOrderFemPy.ts'

uiTranslationFilenamePath = join(translationPath, uiTranslationFilename)
pythonTranslationFilenamePath = join(
    translationPath, pythonTranslationFilename)
defaultTranslationFilenamePath = join(
    translationPath, defaultTranslationFilename)

os.popen(
    '"{}" {} -ts {} -no-ui-lines'.format(
        os.path.join(config('FREECAD'), 'lupdate'),
        uiPath,
        uiTranslationFilenamePath
    )
).read()

allPythonFiles: List[str] = []

getAllPythonFiles('', projectPath, allPythonFiles)

splitAndProcessPythonFiles(allPythonFiles, pythonTranslationFilenamePath)

os.popen(
    '"{}" -i {} {} -o {} -no-ui-lines'.format(
        os.path.join(config('FREECAD'), 'lconvert'),
        uiTranslationFilenamePath,
        pythonTranslationFilenamePath,
        defaultTranslationFilenamePath
    )
).read()

os.remove(uiTranslationFilenamePath)
os.remove(pythonTranslationFilenamePath)

removeUnfinishedTranslations(defaultTranslationFilenamePath)
