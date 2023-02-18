from Imports.flagsAndSettings import *
import os
from tabulate import tabulate

from Utility.mutagenWrapper import AudioFactory, supportedExtensions
from Utility.utilityFunctions import getBest, splitAndGetFirst


def getYearFromDate(date):
    if not date:
        return None
    return date[0:4] if len(date) >= 4 else None


def getOneAudioFile(folderPath):
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() in supportedExtensions:
                return os.path.join(root, file)
    return None


def getSearchTermAndDate(folderPath: str):
    filePath = getOneAudioFile(folderPath)
    if filePath is None:
        return None, None

    audio = AudioFactory.buildAudioManager(filePath)
    albumName = audio.getAlbum()
    date = audio.getDate()
    catalog = audio.getCatalog()
    if catalog:
        return catalog, date
    return albumName, date


def getAlbumTrackData(data, languageOrder):
    trackData = {}
    discNumber = 1
    for disc in data['discs']:
        trackData[discNumber] = {}
        trackNumber = 1
        for track in disc['tracks']:
            trackData[discNumber][trackNumber] = track['names']
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


def doTracksAlign(albumTrackData, folderTrackData, flags: Flags):
    flag = True
    tableData = []
    for discNumber, tracks in albumTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                tableData.append((discNumber, trackNumber, trackTitle, ''))
                flag = False
            else:
                tableData.append((discNumber, trackNumber, getBest(trackTitle, flags.languageOrder), os.path.basename(
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
