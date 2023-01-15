from Imports.flagsAndSettings import *
import os
from tabulate import tabulate

from Utility.mutagenWrapper import AudioFactory
from Utility.utilityFunctions import getBest, splitAndGetFirst


def getOneAudioFile(folderPath):
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() in supportedExtensions:
                return os.path.join(root, file)
    return None


def getAlbumName(folderPath: str):
    filePath = getOneAudioFile(folderPath)
    if filePath is None:
        print('No Audio File Present in the directory to get album name, please provide custom search term!')
        return None

    audio = AudioFactory.buildAudioManager(filePath)
    albumName = audio.getAlbum()
    if albumName is None:
        print('Audio file does not have an <album> tag!, please provide custom search term')
        return None
    return albumName


def getAlbumTrackData(data, languageOrder):
    trackData = {}
    discNumber = 1
    for disc in data['discs']:
        trackData[discNumber] = {}
        trackNumber = 1
        for track in disc['tracks']:
            trackData[discNumber][trackNumber] = getBest(track['names'], languageOrder)
            trackNumber += 1
        discNumber += 1
    return trackData


def getFolderTrackData(folderPath):
    folderTrackData = {}
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() not in supportedExtensions:
                continue
            filePath = os.path.join(root, file)
            audio = AudioFactory.buildAudioManager(filePath)
            discNumber = 1
            trackNumber = 1
            discNumber = audio.getDiscNumber()
            if discNumber is not None:
                discNumber = int(splitAndGetFirst(discNumber))
            else:
                print(f'Disc Number not Present in file : {file}, Taking Default Value = 01')
                discNumber = 1

            trackNumber = audio.getTrackNumber()
            if trackNumber is not None:
                trackNumber = int(splitAndGetFirst(trackNumber))
            else:
                print(f'TrackNumber not Present in file : {file}, Skipped!')
                continue

            if discNumber not in folderTrackData:
                folderTrackData[discNumber] = {}
            if trackNumber in folderTrackData[discNumber]:
                print(
                    f'disc {discNumber}, Track {trackNumber} - {os.path.basename(folderTrackData[discNumber][trackNumber])} Conflicts with {file}')
                continue

            folderTrackData[discNumber][trackNumber] = filePath
    return folderTrackData


def doTracksAlign(albumTrackData, folderTrackData):
    flag = True
    tableData = []
    for discNumber, tracks in albumTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                tableData.append((discNumber, trackNumber, trackTitle, ''))
                flag = False
            else:
                tableData.append((discNumber, trackNumber, trackTitle, os.path.basename(
                    folderTrackData[discNumber][trackNumber])))

    for discNumber, tracks in folderTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in albumTrackData or trackNumber not in albumTrackData[discNumber]:
                tableData.append(
                    (discNumber, trackNumber, '', os.path.basename(
                        folderTrackData[discNumber][trackNumber])))
                flag = False

    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Title', 'fileName'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=53, tablefmt=tableFormat), end='\n\n')
    return flag
