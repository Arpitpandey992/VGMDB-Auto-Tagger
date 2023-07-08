import os
from typing import Optional
from tabulate import tabulate
from mutagen.flac import StreamInfo
from Utility.audioUtils import getFolderTrackData, getOneAudioFile
from Utility.generalUtils import cleanName, fixDate, getProperCount, printAndMoveBack
from Utility.mutagenWrapper import AudioFactory, supportedExtensions, IAudioManager
from Imports.flagsAndSettings import tableFormat
from Utility.template import TemplateResolver
from Utility.generalUtils import get_default_logger

logger = get_default_logger(__name__, 'info')


def countAudioFiles(folderPath: Optional[str] = None, folderTrackData: Optional[dict[int, dict[int, str]]] = None) -> int:
    """
    count the number of audio files present inside a directory (not recursive),
    or return the count of tracks given in folderTrackData format
    """
    if folderTrackData:
        return sum([len(tracks) for _, tracks in folderTrackData.items()])
    if folderPath:
        count = 0
        for filename in os.listdir(folderPath):
            _, extension = os.path.splitext(filename)
            if extension.lower() in supportedExtensions:
                count += 1
        return count
    return 0


def deduceAudioDetails(audio: IAudioManager) -> str:
    extension = audio.getExtension()
    # Flac contains most info variables, hence using it here for type hints only
    info: StreamInfo = audio.getInfo()  # type:ignore
    if extension in ['.flac', '.wav']:
        format = 'FLAC' if extension == '.flac' else 'WAV'
        bits = info.bits_per_sample
        sample_rate = info.sample_rate / 1000
        if sample_rate.is_integer():
            sample_rate = int(sample_rate)
        source = 'CD' if bits == 16 else 'WEB'
        if sample_rate >= 192 or bits > 24:
            source = "VINYL"  # Scuffed way, but assuming Vinyl rips have extremely high sample rate, but Qobuz does provide 192kHz files so yeah...
        # Edge cases should be edited manually later
        return f"{source}-{format} {bits}bit {sample_rate}kHz"
    elif extension == '.mp3':
        # CD-MP3 because in 99% cases, an mp3 album is a lossy cd rip
        bitrate = int(info.bitrate / 1000)
        return f"CD-MP3 {bitrate}kbps"
    elif extension == '.m4a':
        # aac files are usually provided by websites directly for lossy versions. apple music files are also m4a
        bitrate = int(info.bitrate / 1000)
        return f"WEB-AAC {bitrate}kbps"
    elif extension == '.ogg':
        # Usually from spotify
        bitrate = int(info.bitrate / 1000)
        return f"WEB-OGG {bitrate}kbps"
    elif extension == '.opus':
        # YouTube bruh, couldn't figure out a way to retrieve bitrate
        return f"YT-OPUS"
    return ""


def renameAlbumFolder(
    folderPath: str,
    renameTemplate: str
) -> None:
    """rename a folder contains exactly ONE album"""

    filePath = getOneAudioFile(folderPath)
    if not filePath:
        logger.error('no audio file in directory!, aborting')
        return

    audio = AudioFactory.buildAudioManager(filePath)
    folderName = os.path.basename(folderPath)
    albumName = audio.getAlbum()
    if albumName is None and "foldername" not in renameTemplate.lower():
        logger.error(f'no album Name in {filePath}, aborting!')
        return
    date = fixDate(audio.getDate())
    if not date:
        date = fixDate(audio.getCustomTag('year'))
    if date:
        date = date.replace('-', '.')

    templateMapping: dict[str, Optional[str]] = {
        "albumname": albumName,
        "catalog": audio.getCatalog(),
        "date": date,
        "foldername": folderName,
        "barcode": audio.getCustomTag('barcode'),
        "format": deduceAudioDetails(audio)
    }

    templateResolver = TemplateResolver(templateMapping)
    newFolderName = templateResolver.evaluate(renameTemplate)
    newFolderName = cleanName(newFolderName)

    baseFolderPath = os.path.dirname(folderPath)
    newFolderPath = os.path.join(baseFolderPath, newFolderName)
    if (folderName != newFolderName):
        if os.path.exists(newFolderPath):
            logger.error(f'{newFolderName} exists, cannot rename {folderName}')
        else:
            os.rename(folderPath, newFolderPath)
            logger.info(f'rename: {folderName} => {newFolderName}')


def renameAlbumFiles(
    folderPath: str,
    noMove: bool = False,
    verbose: bool = False
):
    """Rename all files present inside a directory which contains files corresponding to ONE album only"""
    folderTrackData = getFolderTrackData(folderPath)
    totalDiscs = len(folderTrackData)

    tableData = []
    for discNumber, tracks in folderTrackData.items():
        totalTracks = len(tracks)
        isSingle = totalTracks == 1
        for trackNumber, filePath in tracks.items():
            fullFileName = os.path.basename(filePath)
            fileName, extension = os.path.splitext(fullFileName)

            audio = AudioFactory.buildAudioManager(filePath)
            title = audio.getTitle()
            if not title:
                logger.error(f'title not present in file: {fileName}, skipped!')
                continue

            trackNumberStr = getProperCount(trackNumber, totalTracks)
            discNumberStr = getProperCount(discNumber, totalDiscs)

            oldName = fullFileName

            if isSingle:
                newName = f"{cleanName(f'{title}')}{extension}"
            else:
                newName = f"{cleanName(f'{trackNumberStr} - {title}')}{extension}"
            discName = audio.getDiscName()

            if discName:
                discFolderName = f'Disc {discNumber} - {discName}'
            else:
                discFolderName = f'Disc {discNumber}'

            if totalDiscs == 1 or noMove:
                discFolderName = ''
            discFolderPath = os.path.join(folderPath, discFolderName)
            if not os.path.exists(discFolderPath):
                os.makedirs(discFolderPath)
            newFilePath = os.path.join(discFolderPath, newName)
            if filePath != newFilePath:
                try:
                    if os.path.exists(newFilePath):
                        logger.error(f'{newFilePath} exists, cannot rename {fileName}')
                    else:
                        os.rename(filePath, newFilePath)
                        printAndMoveBack(f"renamed: {newName}")
                        tableData.append((
                            discNumberStr,
                            trackNumberStr,
                            oldName,
                            os.path.join(discFolderName, newName)
                        ))

                except Exception as e:
                    logger.exception(f'cannot rename {fileName}\n{e}')
    printAndMoveBack('')
    if verbose and tableData:
        logger.info('files renamed as follows:')
        tableData.sort()
        logger.info(
            '\n' + tabulate(
                tableData,
                headers=['Disc', 'Track', 'Old Name', 'New Name'],
                colalign=('center', 'center', 'left', 'left'),
                maxcolwidths=50, tablefmt=tableFormat
            ) + '\n'
        )


def renameFilesRecursively(folderPath, verbose: bool = False, pauseOnFinish: bool = False):
    """
    Rename all files recursively or iteratively in a directory.
    Considers no particular relatioship between files (unlike the albumRename function)
    Does not move files (in Disc folders or anything)
    Use for general folders containing files from various albums
    """
    tableData = []
    renameCount = 1
    for root, dirs, files in os.walk(folderPath):
        totalTracks = countAudioFiles(folderPath=root)
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() not in supportedExtensions:
                logger.info(f"{file} has unsupported extension ({extension})")
                continue
            filePath = os.path.join(root, file)
            audio = AudioFactory.buildAudioManager(filePath)

            title = audio.getTitle()
            if not title:
                logger.info(f'title not present in {file}, skipping!')
                continue
            artist = audio.getArtist()
            date = fixDate(audio.getDate())
            if not date:
                date = fixDate(audio.getCustomTag('year'))
            if date:
                date = date.replace('-', '.')
            year = date[:4] if date and len(date) >= 4 else ""
            oldName = file
            names = {
                1: f"{artist} - {title}{extension}" if artist else f"{title}{extension}",
                2: f"{title}{extension}",
                3: f"[{date}] {title}{extension}",
                4: f"[{year}] {title}{extension}"
            }
            multiTrackName, singleTrackName = 2, 2

            # Change the naming template here :
            # Single here means that the folder itself contains only one file
            isSingle = totalTracks == 1
            nameChoice = singleTrackName if isSingle else multiTrackName

            newName = cleanName(names[nameChoice])

            newFilePath = os.path.join(root, newName)
            if oldName != newName:
                try:
                    if os.path.exists(newFilePath):
                        logger.error(f'{newFilePath} exists, cannot rename {file}')
                    else:
                        os.rename(filePath, newFilePath)
                        printAndMoveBack(f"renamed : {newName}")
                        tableData.append((renameCount, oldName, newName))
                        renameCount += 1
                except Exception as e:
                    logger.exception(f'cannot rename {file}\n{e}')
    printAndMoveBack('')
    if verbose and tableData:
        logger.info('files renamed as follows:')
        tableData.sort()
        logger.info(
            '\n' + tabulate(
                tableData,
                headers=['S.no', 'Old Name', 'New Name'],
                colalign=('center', 'left', 'left'),
                maxcolwidths=45,
                tablefmt=tableFormat
            ) + '\n'
        )
    if pauseOnFinish:
        input("Press Enter to continue...")


def organizeAlbum(folderPath: str, folderNamingtemplate: str, pauseOnFinish: bool = False):
    """Organize a folder which represents ONE album"""
    renameAlbumFiles(folderPath, verbose=True)
    renameAlbumFolder(folderPath, folderNamingtemplate)
    if pauseOnFinish:
        input("Press Enter to continue...")
