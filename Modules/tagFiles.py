import os
import math
from PIL import Image
from tabulate import tabulate

from Modules.flagsAndSettings import Flags
from Modules.utilityFunctions import getBest
from Modules.tagUtilityFunctions import *


def tagFiles(albumTrackData, folderTrackData, data):
    flags: Flags = data['flags']
    albumData = {
        'totalDisks': len(albumTrackData),
        'disksUpperBound': int(math.ceil(math.log10(len(albumTrackData)+1))),
        'albumName': getBest(data['names'], flags.languages),
        'folderPath': data['folderPath'],
        'albumID': data['albumID'],
    }

    # if flags.PICS and 'picture_full' in data:
    #     print('Getting Album Cover')
    #     response = requests.get(data['picture_full'])
    #     image_data = response.content
    #     image = Image.open(io.BytesIO(image_data))
    #     image = image.convert('RGB')  # Remove transparency if present
    #     width, height = image.size

    #     if width > 800:
    #         new_height = int(height * (800 / width))
    #         image = image.resize((800, new_height), resample=Image.LANCZOS)

    #     image_data = io.BytesIO()
    #     image.save(image_data, format='JPEG', quality=70)
    #     image_data = image_data.getvalue()

    #     picture = mutagen.flac.Picture()  # type: ignore
    #     picture.data = image_data
    #     picture.type = 3
    #     picture.mime = 'image/jpeg'

    tableData = []
    for albumData['discNumber'], tracks in albumTrackData.items():

        albumData['totalTracks'] = len(tracks)
        albumData['tracksUpperBound'] = int(
            math.ceil(math.log10(len(tracks)+1)))

        for albumData['trackNumber'], albumData['trackTitle'] in tracks.items():
            if albumData['discNumber'] not in folderTrackData or albumData['trackNumber'] not in folderTrackData[albumData['discNumber']]:
                continue

            albumData['filePath'] = folderTrackData[albumData['discNumber']
                                                    ][albumData['trackNumber']]
            albumData['fileName'] = os.path.basename(albumData['filePath'])
            filePathWithoutExtension, albumData['extension'] = os.path.splitext(
                albumData['fileName'])
            albumData['extension'] = albumData['extension'].lower()

            if albumData['extension'] not in supportedExtensions:
                print(f"Couldn't tag : {albumData['fileName']}")
                tableData.append(
                    ('XX', 'XX', 'XX', albumData['fileName']))
                continue

            audioTagged = False
            if albumData['extension'] == '.flac':
                audioTagged = tagFLAC(data, albumData)

            elif albumData['extension'] == '.mp3':
                audioTagged = tagMP3(data, albumData)

            if audioTagged:
                print(f"Tagged : {albumData['fileName']}")
                tableData.append(
                    (albumData['discNumber'], albumData['trackNumber'], albumData['trackTitle'], albumData['fileName']))
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
