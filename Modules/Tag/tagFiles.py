import os
from tabulate import tabulate
from Imports.config import get_config
from Modules.Scan.models.local_album_data import LocalAlbumData
from Modules.VGMDB.models.vgmdb_album_data import VgmdbAlbumData
from Utility.generalUtils import get_default_logger, printAndMoveBack, updateDict
from Modules.Tag.tagUtils import getImageData, tagAudioFile
from Modules.Mutagen.mutagenWrapper import supportedExtensions
from Utility.generalUtils import getBest

logger = get_default_logger(__name__, "info")


def tagFiles(local_album_data: LocalAlbumData, vgmdb_album_data: VgmdbAlbumData):
    config = get_config()

    totalDiscs = len(albumTrackData)

    tableData = []
    for discNumber, tracks in folderTrackData.items():
        if not config.IGNORE_MISMATCH and discNumber not in albumTrackData:
            continue
        totalTracks = len(albumTrackData.get(discNumber, tracks))

        for trackNumber, filePath in tracks.items():
            if not config.IGNORE_MISMATCH and trackNumber not in albumTrackData.get(discNumber, {}):
                continue
            trackTitles = albumTrackData.get(discNumber, {}).get(trackNumber, {})

            fileName = os.path.basename(filePath)
            _, extension = os.path.splitext(fileName)
            extension = extension.lower()

            if extension not in supportedExtensions:
                logger.error(f"couldn't tag: {fileName}, {extension} Not Supported Yet :(")
                tableData.append(("XX", "XX", "XX", fileName))
                continue

            updateDict(
                trackData,
                {
                    "track_number": trackNumber,
                    "total_tracks": totalTracks,
                    "disc_number": discNumber,
                    "total_discs": totalDiscs,
                    "file_path": filePath,
                    "track_titles": trackTitles,
                },
            )

            audioTagged = tagAudioFile(trackData, config)

            if audioTagged:
                printAndMoveBack(f"Tagged : {fileName}")
                tableData.append((discNumber, trackNumber, getBest(trackTitles, config.language_order), fileName))
            else:
                logger.error(f"couldn't tag: {fileName}")
                tableData.append(("XX", "XX", "XX", fileName))

    if not tableData:
        return
    printAndMoveBack("")
    logger.info("files Tagged as follows:")
    tableData.sort()
    logger.info("\n" + tabulate(tableData, headers=["Disc", "Track", "Title", "File Name"], colalign=("center", "center", "left", "left"), maxcolwidths=50, tablefmt=Configs().tableFormat))
