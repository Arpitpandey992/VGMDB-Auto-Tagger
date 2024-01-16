from Imports.config import Config
import os
from tabulate import tabulate
from typing import Optional
from Modules.Mutagen.mutagenWrapper import supportedExtensions
from Modules.VGMDB.models.vgmdb_album_data import VgmdbAlbumData
from Types.otherData import OtherData
from Modules.Mutagen.mutagenWrapper import AudioFactory
from Modules.Translate.translator import translate
from Modules.Utils.general_utils import get_default_logger, getBest

logger = get_default_logger(__name__, "info")


def getYearFromDate(date: Optional[str]) -> Optional[str]:
    if not date:
        return None
    return date[0:4] if len(date) >= 4 else None


def getOneAudioFile(folderPath: str) -> Optional[str]:
    for root, dirs, files in sorted(os.walk(folderPath)):
        for file in sorted(files):
            _, extension = os.path.splitext(file)
            if extension.lower() in supportedExtensions:
                return os.path.join(root, file)
    return None


def getSearchTermAndDate(folderPath: str) -> tuple[Optional[str], Optional[str]]:
    filePath = getOneAudioFile(folderPath)
    if filePath is None:
        return None, None

    audio = AudioFactory.buildAudioManager(filePath)
    possibleValues = [audio.getCatalog(), audio.getCustomTag("barcode"), audio.getAlbum()]
    date = audio.getDate()
    for value in possibleValues:
        if value:
            return value, date
    return None, date


def getAlbumTrackData(albumData: VgmdbAlbumData) -> dict[int, dict[int, dict[str, str]]]:
    flags = Config()
    trackData: dict[int, dict[int, dict[str, str]]] = {}
    discNumber = 1
    for disc in albumData["discs"]:
        trackData[discNumber] = {}
        trackNumber = 1
        for track in disc["tracks"]:
            names = {key: val for key, val in track["names"].items() if val != "None"}
            if flags.translate:
                # Translating when english is not present
                otherLanguageTitle = getBest(names, flags.language_order)
                translateObject = translate(otherLanguageTitle, "english")
                englishName = translateObject["translatedText"]
                romajiName = translateObject["romajiText"]
                if englishName:
                    names["English Translated"] = englishName
                if romajiName:
                    names["Romaji Translated"] = romajiName

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
                logger.error(f"track number not present in file: {file}, skipped!")
                continue

            discNumber = audio.getDiscNumber()
            if discNumber is None:
                logger.error(f"disc number not present in file: {file}, taking default value = 1")
                discNumber = 1
            trackNumber, discNumber = int(trackNumber), int(discNumber)

            if discNumber not in folderTrackData:
                folderTrackData[discNumber] = {}
            if trackNumber in folderTrackData[discNumber]:
                logger.error(f"disc {discNumber}, track {trackNumber} - {os.path.basename(folderTrackData[discNumber][trackNumber])} conflicts with {file}")
                continue

            folderTrackData[discNumber][trackNumber] = filePath
    return folderTrackData


def doTracksAlign(albumTrackData: dict[int, dict[int, dict[str, str]]], folderTrackData: dict[int, dict[int, str]], flags: Config) -> bool:
    flag = True
    tableData = []
    for discNumber, tracks in albumTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                tableData.append((discNumber, trackNumber, getBest(trackTitle, flags.language_order), ""))
                flag = False
            else:
                tableData.append((discNumber, trackNumber, getBest(trackTitle, flags.language_order), os.path.basename(folderTrackData[discNumber][trackNumber])))

    for discNumber, tracks in folderTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in albumTrackData or trackNumber not in albumTrackData[discNumber]:
                tableData.append((discNumber, trackNumber, "", os.path.basename(folderTrackData[discNumber][trackNumber])))
                flag = False

    tableData.sort()
    logger.info(
        "\n"
        + tabulate(
            tableData,
            headers=["Disc", "Track", "Title (Translated)" if flags.translate else "Title", "fileName"],
            colalign=("center", "center", "left", "left"),
            maxcolwidths=50,
            tablefmt=Config().table_format,
        )
    )
    return flag
