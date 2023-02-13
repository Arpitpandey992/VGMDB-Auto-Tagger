import os
import math
from PIL import Image
from tabulate import tabulate

from Imports.flagsAndSettings import Flags, tableFormat
from Utility.utilityFunctions import getBest
from Modules.Tag.tagUtilityFunctions import tagAudioFile
from Utility.mutagenWrapper import supportedExtensions


def tagFiles(albumTrackData, folderTrackData, data):
    flags: Flags = data['flags']
    albumData = {
        'totalDiscs': len(albumTrackData),
        # 'discsUpperBound': int(math.ceil(math.log10(len(albumTrackData)+1))),
        'albumName': getBest(data['names'], flags.languageOrder),
        'folderPath': data['folderPath'],
        'albumID': data['albumID'],
    }

    tableData = []
    for albumData['discNumber'], tracks in albumTrackData.items():

        albumData['totalTracks'] = len(tracks)
        # albumData['tracksUpperBound'] = int(
        #     math.ceil(math.log10(len(tracks)+1)))

        for albumData['trackNumber'], albumData['trackTitle'] in tracks.items():
            if albumData['discNumber'] not in folderTrackData or albumData['trackNumber'] not in folderTrackData[albumData['discNumber']]:
                continue

            albumData['filePath'] = folderTrackData[albumData['discNumber']
                                                    ][albumData['trackNumber']]
            albumData['fileName'] = os.path.basename(albumData['filePath'])
            filePathWithoutExtension, albumData['extension'] = os.path.splitext(albumData['fileName'])
            albumData['extension'] = albumData['extension'].lower()

            if albumData['extension'] not in supportedExtensions:
                print(f"Couldn't tag : {albumData['fileName']}, {albumData['extension']} Not Supported Yet :(")
                tableData.append(
                    ('XX', 'XX', 'XX', albumData['fileName']))
                continue

            # Tagging the file
            audioTagged = tagAudioFile(data, albumData)

            if audioTagged:
                print(f"Tagged : {albumData['fileName']}")
                tableData.append((albumData['discNumber'], albumData['trackNumber'], albumData['trackTitle'], albumData['fileName']))
            else:
                print(f"Couldn't tag : {albumData['fileName']}")
                tableData.append(
                    ('XX', 'XX', 'XX', albumData['fileName']))

    if not tableData:
        return
    print('\n', end='')

    print('Files Tagged as follows')
    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Title', 'File Name'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=53, tablefmt=tableFormat), end='\n\n')
