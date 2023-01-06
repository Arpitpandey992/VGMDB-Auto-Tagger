import os
import requests
import mutagen
import math
import io
from PIL import Image


from flagsAndSettings import *
from utilityFunctions import *
from vgmdbrip.vgmdbrip import getPictures


def tagFiles(albumTrackData, folderTrackData, data, languages):

    totalDisks = len(albumTrackData)
    disksUpperBound = int(math.ceil(math.log10(totalDisks+1)))
    albumName = getBest(data['names'], languages)
    folderPath = data['folderPath']
    albumID = data['albumID']

    if PICS or SCANS:
        print('Downloading Pictures')
        if(PICS and 'picture_full' in data):
            response = requests.get(data['picture_full'])
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGB')
            width, height = image.size

            if width > 800:
                new_height = int(height * (800 / width))
                image = image.resize((800, new_height), resample=Image.LANCZOS)

            image_data = io.BytesIO()
            image.save(image_data, format='JPEG', quality=70)
            # The above line does sometimes fail, but it is better to keep it. Try catch makes it fail all the time
            #image.save(image_data, format='PNG', quality=70)

            image_data = image_data.getvalue()

            picture = mutagen.flac.Picture()  # type: ignore
            picture.data = image_data
            picture.type = 3
            picture.mime = 'image/jpeg'
        if SCANS:
            getPictures(folderPath, albumID)
        print('Downloaded Available Pictures :)', end='\n\n')
        # old algorithm for downloading -> no Login -> less covers available!
        if(False and SCANS and 'covers' in data):
            frontPictureExists = False
            coverPath = os.path.join(data['folderPath'], 'Scans')
            if not os.path.exists(coverPath):
                os.makedirs(coverPath)
            for cover in data['covers']:
                downloadPicture(URL=cover['full'],
                                path=coverPath, name=cover['name'])
                if cover['name'].lower() == 'front' or cover['name'].lower == 'cover':
                    frontPictureExists = True
            if not frontPictureExists and 'picture_full' in data:
                downloadPicture(URL=data['picture_full'],
                                path=coverPath, name='Front')
            print('Done.')
            print('\n', end='')

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

            if DATE and 'release_date' in data:
                audio['date'] = standardize_date(data['release_date'])

            audio['album'] = albumName

            # These tags are not supported for MP3 files (in this program), Sorry :(
            if isFLAC:
                if(PICS and 'picture_full' in data and not hasCoverOfType(audio, 3)):
                    audio.add_picture(picture)  # type: ignore
                audio['tracktotal'] = str(totalTracks)
                audio['disctotal'] = str(totalDisks)
                audio['comment'] = f"Find the tracklist at {data['albumLink']}"

                if YEAR and 'release_date' in data and len(data['release_date']) >= 4:
                    audio['year'] = data['release_date'][0:4]

                if CATALOG and 'catalog' in data:
                    audio['catalog'] = data['catalog']

                if BARCODE and 'barcode' in data:
                    audio['barcode'] = data['barcode']

                if ORGANIZATIONS and 'organizations' in data:
                    for org in data['organizations']:
                        audio[org['role']] = getBest(org['names'], languages)

                def addMultiValues(tag, tagInFile, flag=True):
                    if tag in data and flag:
                        temp = []
                        for val in data[tag]:
                            temp.append(getBest(val['names'], languages))
                        audio[tagInFile] = temp

                addMultiValues('lyricists', 'lyricist', LYRICISTS)
                addMultiValues('performers', 'performer', PERFORMERS)
                addMultiValues('arrangers', 'arranger', ARRANGERS)
                addMultiValues('composers', 'composer', COMPOSERS)

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
