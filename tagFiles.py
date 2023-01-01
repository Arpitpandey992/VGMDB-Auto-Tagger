import os
import requests
import mutagen
import math

from flagsAndSettings import *
from utilityFunctions import *


def tagFiles(albumTrackData, folderTrackData, data):

    totalTracks = 0
    for disc in albumTrackData:
        totalTracks += len(albumTrackData[disc])
    totalDisks = len(albumTrackData)
    tracksUpperBound = int(math.ceil(math.log10(totalTracks+1)))
    disksUpperBound = int(math.ceil(math.log10(totalDisks+1)))
    albumName = getBest(data['names'])

    if PICS or SCANS:
        print('Downloading Pictures')
        if(PICS and 'picture_full' in data):
            response = requests.get(data['picture_full'])
            image_data = response.content
            picture = mutagen.flac.Picture()
            picture.data = image_data
            picture.type = 3
            picture.mime = 'image/jpeg'

        if(SCANS and 'covers' in data):
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
                    audio.add_picture(picture)

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
                        audio[org['role']] = getBest(org['names'])

                def addMultiValues(tag, tagInFile, flag=True):
                    if tag in data and flag:
                        temp = []
                        for val in data[tag]:
                            temp.append(getBest(val['names']))
                        audio[tagInFile] = temp

                addMultiValues('lyricists', 'lyricist', LYRICISTS)
                addMultiValues('performers', 'performer', PERFORMERS)
                addMultiValues('arrangers', 'arranger', ARRANGERS)
                addMultiValues('composers', 'composer', COMPOSERS)

            # Tagging track specific details

            audio['title'] = trackTitle
            audio['discnumber'] = str(discNumber).zfill(disksUpperBound)
            audio['tracknumber'] = str(trackNumber).zfill(tracksUpperBound)

            audio.save()
            tableData.append(
                (discNumber, trackNumber, trackTitle, fileName))
    
    print('Files Tagged as follows')
    print('\n', end='')
    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Title', 'File Name'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=60, tablefmt=tableFormat), end='\n\n')
    return True
