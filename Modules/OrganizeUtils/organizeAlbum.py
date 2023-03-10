import os

from Utility.mutagenWrapper import AudioFactory, supportedExtensions
from Utility.utilityFunctions import getProperCount, cleanName
from Utility.audioUtilityFunctions import getOneAudioFile
from Modules.Tag.tagUtilityFunctions import standardizeDate

"""
Organize a single album contained in a single folder. 
This will rename the files within the folder and appropriately rename the folder
"""


def renameAndOrganizeFiles(folderPath):
    used = set()
    for root, dirs, files in os.walk(folderPath):
        for file in sorted(files):
            _, extension = os.path.splitext(file)
            if extension.lower() not in supportedExtensions:
                continue
            filePath = os.path.join(root, file)
            audio = AudioFactory.buildAudioManager(filePath)
            trackNumber = audio.getTrackNumber()
            discNumber = audio.getDiscNumber()
            title = audio.getTitle()
            totalTracks = audio.getTotalTracks()
            totalDiscs = audio.getTotalDiscs()
            if trackNumber is None:
                print(f'TrackNumber not Present in file : {file} Skipped!')
                continue
            if title is None:
                print(f'Title not Present in file : {file} Skipped!')
                continue
            if discNumber is None:
                print(f'DiscNumber not Present in file : {file} taking default value = 1')
                discNumber = '1'

            if totalTracks is None:
                totalTracks = '99'

            if totalDiscs is None:
                totalDiscs = '1'
            trackNumber = getProperCount(trackNumber, totalTracks)
            discNumber = getProperCount(discNumber, totalDiscs)
            discTrackTuple = (int(discNumber), int(trackNumber))
            if discTrackTuple in used:
                print(f'Disc {discNumber}, Track {trackNumber} Already Renamed!, {file} Skipped!')
                continue
            used.add(discTrackTuple)

            oldName = file
            newName = cleanName(f"{trackNumber} - {title}{extension}")
            discName = audio.getDiscName()

            if discName:
                discFolderName = f'Disc {discNumber} - {discName}'
            else:
                discFolderName = f'Disc {discNumber}'

            if int(totalDiscs) == 1:
                # no need to make separate disc folders
                discFolderName = ''
            discFolderPath = os.path.join(folderPath, discFolderName)
            if not os.path.exists(discFolderPath):
                os.makedirs(discFolderPath)
            newFilePath = os.path.join(discFolderPath, newName)
            if filePath != newFilePath:
                try:
                    if os.path.exists(newFilePath):
                        print(f'{newFilePath} Exists, cannot rename {file}')
                    else:
                        os.rename(filePath, newFilePath)
                        print(f'Renamed {oldName} to {discFolderName}/{newName}')
                except Exception as e:
                    print(f'Cannot rename {file}')
                    print(e)


def renameFolder(folderPath, sameFolderName: bool = False):
    filePath = getOneAudioFile(folderPath)
    if filePath is None:
        print('No Audio file in directory!, aborting')
        return
    audio = AudioFactory.buildAudioManager(filePath)
    if sameFolderName:
        albumName = os.path.basename(folderPath)
    else:
        albumName = audio.getAlbum()
        if albumName is None:
            print(f'No Album Name in {filePath}, aborting')
            return
    date = standardizeDate(audio.getDate())
    if date == "":
        date = standardizeDate(audio.getCustomTag('year'))
    date = date.replace('-', '.')
    catalog = audio.getCatalog()
    newFolderName = albumName
    if catalog and date:
        newFolderName = f'[{date}] {albumName} [{catalog}]'
        # newFolderName = f'[{catalog]}] {albumName} [{date}]'
    elif catalog:
        newFolderName = f'{albumName} [{catalog}]'
    elif date:
        newFolderName = f'[{date}] {albumName}'
    else:
        newFolderName = f'{albumName}'

    oldFolderName = os.path.basename(folderPath)
    newFolderName = cleanName(newFolderName)

    baseFolderPath = os.path.dirname(folderPath)
    newFolderPath = os.path.join(baseFolderPath, newFolderName)
    if (oldFolderName != newFolderName):
        os.rename(folderPath, newFolderPath)
        print(f'Successfully Renamed {oldFolderName} to {newFolderName}')


def organizeAlbum(folderPath, sameFolderName: bool = False):
    print(f'Organizing Album : {os.path.basename(folderPath)}')
    renameAndOrganizeFiles(folderPath)
    renameFolder(folderPath, sameFolderName)
    print(f'{os.path.basename(folderPath)} Organized!')
    print('\n', end='')
