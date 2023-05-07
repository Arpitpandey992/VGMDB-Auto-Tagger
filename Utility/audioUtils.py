from Imports.flagsAndSettings import Flags, tableFormat
import os
from tabulate import tabulate
from typing import Optional
from Types.albumData import AlbumData
from Types.otherData import OtherData
from Utility.mutagenWrapper import AudioFactory, supportedExtensions
from Utility.generalUtils import getBest, isLanguagePresent
from Utility.translator import translate


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
    possibleValues = [audio.getCatalog(), audio.getCustomTag('barcode'), audio.getAlbum()]
    date = audio.getDate()
    for value in possibleValues:
        if value:
            return value, date
    return None, date


def getAlbumTrackData(albumData: AlbumData, otherData: OtherData) -> dict[int, dict[int, dict[str, str]]]:
    flags: Flags = otherData['flags']
    trackData: dict[int, dict[int, dict[str, str]]] = {}
    discNumber = 1
    for disc in albumData['discs']:
        trackData[discNumber] = {}
        trackNumber = 1
        for track in disc['tracks']:
            names = track['names']
            if flags.TRANSLATE:
                # Translating when english is not present
                otherLanguageTitle = list(names.items())[0][1]
                translateObject = translate(otherLanguageTitle, 'english')
                englishName = translateObject['translatedText']
                romajiName = translateObject['romajiText']
                if englishName:
                    names['English Translated'] = englishName
                if romajiName:
                    names['Romaji Translated'] = romajiName

            trackData[discNumber][trackNumber] = names
            trackNumber += 1
        discNumber += 1
    return trackData


def getFolderTrackData(folderPath: str) -> dict[int, dict[int, str]]:
    folderTrackData: dict[int, dict[int, str]] = {}
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
    albumTrackData: dict[int, dict[int, dict[str, str]]],
    folderTrackData: dict[int, dict[int, str]],
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
