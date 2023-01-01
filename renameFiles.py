import math
import shutil

from flagsAndSettings import *
from utilityFunctions import *

forbiddenCharacters = {
    '<': 'ᐸ',
    '>': 'ᐳ',
    ':': '꞉',
    '"': 'ˮ',
    '/': '᜵',
    '\\': '∖',
    '|': 'ǀ',
    '?': 'ʔ',
    '*': '∗',
    '+': '᛭',
    '%': '٪',
    '!': 'ⵑ',
    '`': '՝',
    '&': 'ꝸ',
    '{': '❴',
    '}': '❵',
    '=': '᐀',
    '#': '#',  # couldn't find alternative
    '$': '$',  # couldn't find alternative
    '@': '@'  # couldn't find alternative
}


def cleanName(name):
    output = name
    for invalidCharacter, validAlternative in forbiddenCharacters.items():
        output = output.replace(invalidCharacter, validAlternative)
    return output


def renameFiles(albumTrackData, folderTrackData, data):
    totalTracks = 0
    for disc in albumTrackData:
        totalTracks += len(albumTrackData[disc])
    totalDisks = len(albumTrackData)
    tracksUpperBound = int(math.ceil(math.log10(totalTracks+1)))
    disksUpperBound = int(math.ceil(math.log10(totalDisks+1)))
    albumName = getBest(data['names'])
    folderPath = data['folderPath']

    for discNumber, tracks in folderTrackData.items():
        properDiscNumber = str(discNumber).zfill(disksUpperBound)
        if totalDisks > 1:
            discFolderPath = os.path.join(
                folderPath, f'Disc {properDiscNumber}')
            baseDiscFolder = os.path.basename(discFolderPath)
        else:
            discFolderPath = folderPath
            baseDiscFolder = ''
        if not os.path.exists(discFolderPath):
            os.makedirs(discFolderPath)
        tableData = []
        for trackNumber, filePath in folderTrackData[discNumber].items():
            fileName = os.path.basename(filePath)
            fileNameWithPath, extension = os.path.splitext(filePath)
            properTrackNumber = str(trackNumber).zfill(tracksUpperBound)
            if discNumber not in albumTrackData or trackNumber not in albumTrackData[discNumber]:
                tableData.append(
                    (discNumber, trackNumber, fileName, '**NO CHANGE**'))
                continue
            newName = cleanName(albumTrackData[discNumber][trackNumber])
            finalNewName = f'{properTrackNumber}. {newName}{extension}'
            newPath = os.path.join(discFolderPath, finalNewName)
            shutil.move(filePath, newPath)
            tableData.append(
                (discNumber, trackNumber, fileName, os.path.join(baseDiscFolder, finalNewName)))

    print('Files Renamed as Follows\n')
    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Old Name', 'New Name'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=60, tablefmt=tableFormat), end='\n\n')
