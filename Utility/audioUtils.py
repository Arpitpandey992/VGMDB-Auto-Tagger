from Imports.flagsAndSettings import *
import os
from tabulate import tabulate
from typing import Dict, Optional
from Types.albumData import AlbumData
from Types.otherData import OtherData
from Utility.mutagenWrapper import AudioFactory, supportedExtensions
from Utility.generalUtils import getBest
from Utility.translate import translate


def getYearFromDate(date: Optional[str]) -> Optional[str]:
    if not date:
        return None
    return date[0:4] if len(date) >= 4 else None


def getOneAudioFile(folderPath: str) -> Optional[str]:
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() in supportedExtensions:
                return os.path.join(root, file)
    return None


def getSearchTermAndDate(folderPath: str) -> tuple[Optional[str], Optional[str]]:
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


def getAlbumTrackData(albumData: AlbumData, otherData: OtherData) -> Dict[int, Dict[int, Dict[str, str]]]:
    flags: Flags = otherData['flags']
    trackData: Dict[int, Dict[int, Dict[str, str]]] = {}
    discNumber = 1
    for disc in albumData['discs']:
        trackData[discNumber] = {}
        trackNumber = 1
        for track in disc['tracks']:
            names = track['names']
            # This is pretty dangerous, Do not translate unless absolutely sure
            if flags.TRANSLATE:
                for lang, trackName in names.items():
                    names[lang] = translate(trackName)
            trackData[discNumber][trackNumber] = names
            trackNumber += 1
        discNumber += 1
    return trackData


def getFolderTrackData(folderPath: str) -> Dict[int, Dict[int, str]]:
    folderTrackData: Dict[int, Dict[int, str]] = {}
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() not in supportedExtensions:
                continue
            filePath = os.path.join(root, file)
            audio = AudioFactory.buildAudioManager(filePath)

            trackNumber = audio.getTrackNumber()
            if trackNumber is None:
                print(f'TrackNumber not Present in file : {file}, Skipped!')
                continue

            discNumber = audio.getDiscNumber()
            if discNumber is None:
                print(f'Disc Number not Present in file : {file}, Taking Default Value = 01')
                discNumber = 1
            trackNumber, discNumber = int(trackNumber), int(discNumber)

            if discNumber not in folderTrackData:
                folderTrackData[discNumber] = {}
            if trackNumber in folderTrackData[discNumber]:
                print(f'disc {discNumber}, Track {trackNumber} - {os.path.basename(folderTrackData[discNumber][trackNumber])} Conflicts with {file}')
                continue

            folderTrackData[discNumber][trackNumber] = filePath
    return folderTrackData


def doTracksAlign(
    albumTrackData: Dict[int, Dict[int, Dict[str, str]]],
    folderTrackData: Dict[int, Dict[int, str]],
    flags: Flags
) -> bool:
    flag = True
    tableData = []
    for discNumber, tracks in albumTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                tableData.append((discNumber, trackNumber, getBest(trackTitle, flags.languageOrder), ''))
                flag = False
            else:
                tableData.append((discNumber, trackNumber, getBest(trackTitle, flags.languageOrder), os.path.basename(
                    folderTrackData[discNumber][trackNumber])))

    for discNumber, tracks in folderTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in albumTrackData or trackNumber not in albumTrackData[discNumber]:
                tableData.append((
                    discNumber,
                    trackNumber,
                    '',
                    os.path.basename(folderTrackData[discNumber][trackNumber])
                ))
                flag = False

    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Title (Translated)' if flags.TRANSLATE else 'Title', 'fileName'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=50, tablefmt=tableFormat), end='\n\n')
    return flag
