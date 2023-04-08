import os
from tabulate import tabulate
from Imports.flagsAndSettings import tableFormat
from Types.albumData import AlbumData, TrackData
from Types.otherData import OtherData
from Utility.generalUtils import getBest, printAndMoveBack, updateDict
from Modules.Tag.tagUtils import getImageData, tagAudioFile
from Utility.mutagenWrapper import supportedExtensions


def tagFiles(
    albumTrackData: dict[int, dict[int, dict[str, str]]],
    folderTrackData: dict[int, dict[int, str]],
    albumData: AlbumData,
    otherData: OtherData
):
    flags = otherData.get('flags')
    trackData: TrackData = {
        **albumData,
        'track_number': 0,
        'total_tracks': 0,
        'disc_number': 0,
        'total_discs': 0,
        'file_path': "",
        'track_titles': {},
        'album_link': albumData.get('vgmdb_link'),
        'album_names': albumData.get('names'),
        'album_name': getBest(albumData.get('names'), flags.languageOrder),
    }
    if flags.PICS:
        imageData = getImageData(albumData)
        if imageData:
            trackData['picture_cache'] = imageData
    totalDiscs = len(albumTrackData)

    tableData = []
    for discNumber, tracks in folderTrackData.items():
        if not flags.IGNORE_MISMATCH and discNumber not in albumTrackData:
            continue
        totalTracks = len(albumTrackData.get(discNumber, tracks))

        for trackNumber, filePath in tracks.items():
            if not flags.IGNORE_MISMATCH and trackNumber not in albumTrackData.get(discNumber, {}):
                continue
            trackTitles = albumTrackData.get(discNumber, {}).get(trackNumber, {})

            fileName = os.path.basename(filePath)
            _, extension = os.path.splitext(fileName)
            extension = extension.lower()

            if extension not in supportedExtensions:
                print(f"Couldn't tag : {fileName}, {extension} Not Supported Yet :(")
                tableData.append(('XX', 'XX', 'XX', fileName))
                continue

            updateDict(trackData, {
                'track_number': trackNumber,
                'total_tracks': totalTracks,
                'disc_number': discNumber,
                'total_discs': totalDiscs,
                'file_path': filePath,
                'track_titles': trackTitles,
            })

            audioTagged = tagAudioFile(trackData, flags)

            if audioTagged:
                printAndMoveBack(f"Tagged : {fileName}")
                tableData.append((
                    discNumber,
                    trackNumber,
                    getBest(trackTitles, flags.languageOrder),
                    fileName
                ))
            else:
                print(f"Couldn't tag : {fileName}")
                tableData.append(('XX', 'XX', 'XX', fileName))

    if not tableData:
        return
    printAndMoveBack('')
    print('Files Tagged as follows:')
    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Title', 'File Name'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=50, tablefmt=tableFormat), end='\n\n')
