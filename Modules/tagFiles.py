import os
import requests
import mutagen
import math
import io
from PIL import Image


from Modules.flagsAndSettings import *
from Modules.utilityFunctions import *
from Modules.vgmdbrip.vgmdbrip import getPictures


def tagFiles(albumTrackData, folderTrackData, data):
    flags: Flags = data['flags']

    totalDisks = len(albumTrackData)
    disksUpperBound = int(math.ceil(math.log10(totalDisks+1)))
    albumName = getBest(data['names'], flags.languages)
    folderPath = data['folderPath']
    albumID = data['albumID']

    if flags.PICS and 'picture_full' in data:
        print('Getting Album Cover')
        response = requests.get(data['picture_full'])
        image_data = response.content
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('RGB')  # Remove transparency if present
        width, height = image.size

        if width > 800:
            new_height = int(height * (800 / width))
            image = image.resize((800, new_height), resample=Image.LANCZOS)

        image_data = io.BytesIO()
        image.save(image_data, format='JPEG', quality=70)
        image_data = image_data.getvalue()

        picture = mutagen.flac.Picture()  # type: ignore
        picture.data = image_data
        picture.type = 3
        picture.mime = 'image/jpeg'

    tableData = []
    for discNumber, tracks in albumTrackData.items():
        totalTracks = len(tracks)
        tracksUpperBound = int(math.ceil(math.log10(totalTracks+1)))
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                continue

            filePath = folderTrackData[discNumber][trackNumber]
            fileName = os.path.basename(filePath)
            audio = openMutagenFile(filePath)
            isFLAC = fileName.lower().endswith('.flac')
            # Tagging Album specific Details

            if flags.DATE and 'release_date' in data:
                audio['date'] = standardize_date(data['release_date'])

            audio['album'] = albumName

            # These tags are not supported for MP3 files (in this program), Sorry :(
            if isFLAC:
                if(flags.PICS and 'picture_full' in data and not hasCoverOfType(audio, 3)):
                    audio.add_picture(picture)  # type: ignore
                audio['tracktotal'] = str(totalTracks)
                audio['disctotal'] = str(totalDisks)
                audio['comment'] = f"Find the tracklist at {data['albumLink']}"

                if flags.YEAR and 'release_date' in data and len(data['release_date']) >= 4:
                    audio['year'] = data['release_date'][0:4]

                if flags.CATALOG and 'catalog' in data:
                    audio['catalog'] = data['catalog']

                if flags.BARCODE and 'barcode' in data:
                    audio['barcode'] = data['barcode']

                if flags.ORGANIZATIONS and 'organizations' in data:
                    for org in data['organizations']:
                        audio[org['role']] = getBest(
                            org['names'], flags.languages)

                def addMultiValues(tag, tagInFile, flag=True):
                    if tag in data and flag:
                        temp = []
                        for val in data[tag]:
                            temp.append(getBest(val['names'], flags.languages))
                        audio[tagInFile] = temp

                addMultiValues('lyricists', 'lyricist', flags.LYRICISTS)
                addMultiValues('performers', 'performer', flags.PERFORMERS)
                addMultiValues('arrangers', 'arranger', flags.ARRANGERS)
                addMultiValues('composers', 'composer', flags.COMPOSERS)

            # Tagging track specific details

            audio['title'] = trackTitle
            audio['discnumber'] = str(discNumber).zfill(disksUpperBound)
            audio['tracknumber'] = str(trackNumber).zfill(tracksUpperBound)
            print(f'Tagged : {fileName}')
            audio.save()
            tableData.append(
                (discNumber, trackNumber, trackTitle, fileName))
    print('\n', end='')

    print('Files Tagged as follows')
    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Title', 'File Name'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=53, tablefmt=tableFormat), end='\n\n')
    return True
