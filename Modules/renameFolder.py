import os
from Modules.flagsAndSettings import Flags
from Modules.utilityFunctions import getBest, cleanName


def renameFolder(data):
    flags: Flags = data['flags']
    albumName = cleanName(getBest(data['names'], flags.languageOrder))
    folderPath = data['folderPath']
    date = data['release_date'].replace('-', '.')

    if 'catalog' in data and data['catalog'] != 'N/A':
        newFolderName = f'[{date}] {albumName} [{data["catalog"]}]'
        # newFolderName = f'[{data["catalog"]}] {albumName} [{date}]'
    else:
        newFolderName = f'[{date}] {albumName}'

    oldFolderName = os.path.basename(folderPath)
    baseFolderPath = os.path.dirname(folderPath)
    newFolderPath = os.path.join(baseFolderPath, newFolderName)
    os.rename(folderPath, newFolderPath)
    print(f'Successfully Renamed {oldFolderName} to {newFolderName}')
    print('\n', end='')
