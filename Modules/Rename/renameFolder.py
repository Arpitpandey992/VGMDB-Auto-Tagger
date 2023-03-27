import os
from Imports.flagsAndSettings import Flags
from Types.albumData import AlbumData
from Types.otherData import OtherData
from Utility.utilityFunctions import getBest, cleanName


def renameFolder(albumData: AlbumData, otherData: OtherData):
    flags: Flags = otherData['flags']
    albumName = getBest(albumData['names'], flags.languageOrder)
    folderPath = otherData['folder_path']
    date = albumData['release_date'].replace('-', '.')

    if 'catalog' in albumData and albumData['catalog'] != 'N/A':
        newFolderName = f'[{date}] {albumName} [{albumData["catalog"]}]'
        newFolderName = f'[{albumData["catalog"]}] {albumName} [{date}]'
    else:
        newFolderName = f'[{date}] {albumName}'

    newFolderName = cleanName(newFolderName)
    oldFolderName = os.path.basename(folderPath)

    baseFolderPath = os.path.dirname(folderPath)
    newFolderPath = os.path.join(baseFolderPath, newFolderName)
    os.rename(folderPath, newFolderPath)
    print(f'Successfully Renamed {oldFolderName} to {newFolderName}')
    print('\n', end='')
