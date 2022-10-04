import os
import shutil


def join(arg1, arg2):
    return os.path.join(arg1, arg2)


def removePyCacheFolderRecursively(fileOrFolder, sourcePath):
    fullFileFolderPath = join(sourcePath, fileOrFolder)

    if fileOrFolder == '__pycache__':
        shutil.rmtree(fullFileFolderPath)
        return

    if os.path.isfile(fullFileFolderPath):
        return

    if os.path.isdir(fullFileFolderPath):
        subFilesOrFolders = os.listdir(fullFileFolderPath)

        for subFileOrFolder in subFilesOrFolders:
            removePyCacheFolderRecursively(
                subFileOrFolder,
                fullFileFolderPath
            )


projectPath = join(os.path.dirname(__file__), '..')

removePyCacheFolderRecursively('', projectPath)
