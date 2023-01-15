import shutil
import os

from Imports.flagsAndSettings import tableFormat
from Utility.utilityFunctions import getProperCount, cleanName
from tabulate import tabulate

def renameFiles(albumTrackData, folderTrackData, data):
    # flags: Flags = data['flags']

    totalTracks = 0
    for disc in albumTrackData:
        totalTracks += len(albumTrackData[disc])
    totalDiscs = len(albumTrackData)
    # discsUpperBound = int(math.ceil(math.log10(totalDiscs+1)))
    # albumName = cleanName(getBest(data['names'], flags.languageOrder))
    folderPath = data['folderPath']
    # date = data['release_date'].replace('-', '.')

    tableData = []
    for discNumber, tracks in folderTrackData.items():
        # tracksUpperBound = int(math.ceil(math.log10(len(tracks)+1)))
        properDiscNumber = getProperCount(discNumber, totalDiscs)
        # properDiscNumber = str(discNumber).zfill(discsUpperBound)
        if totalDiscs > 1:
            discFolderPath = os.path.join(
                folderPath, f'Disc {properDiscNumber}')
            baseDiscFolder = os.path.basename(discFolderPath)
        else:
            discFolderPath = folderPath
            baseDiscFolder = ''
        if not os.path.exists(discFolderPath):
            os.makedirs(discFolderPath)
        for trackNumber, filePath in folderTrackData[discNumber].items():
            fileName = os.path.basename(filePath)
            fileNameWithPath, extension = os.path.splitext(filePath)
            properTrackNumber = getProperCount(trackNumber, len(tracks))
            # properTrackNumber = str(trackNumber).zfill(tracksUpperBound)
            if discNumber not in albumTrackData or trackNumber not in albumTrackData[discNumber]:
                tableData.append(
                    (discNumber, trackNumber, fileName, '**NO CHANGE**'))
                continue
            newName = cleanName(albumTrackData[discNumber][trackNumber])
            # File Names
            finalNewName = f'{properTrackNumber} - {newName}{extension}'
            newPath = os.path.join(discFolderPath, finalNewName)
            shutil.move(filePath, newPath)
            tableData.append(
                (discNumber, trackNumber, fileName, os.path.join(baseDiscFolder, ' '+finalNewName)))

    if not tableData:
        return

    print('Files Renamed as Follows\n')
    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Old Name', 'New Name'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=53, tablefmt=tableFormat), end='\n\n')
