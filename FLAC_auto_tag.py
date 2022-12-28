import os
import json
import requests
import math
import mutagen
from mutagen.flac import FLAC

# languages to be probed from VGMDB in the given order of priority
languages = ['en', 'English', 'ja-latn', 'Romaji', 'ja', 'Japanese']

################## Helper Functions ############################


def standardize_date(date_string: str) -> str:
    # Split the date string into its components
    date_components = date_string.split('-')
    num_components = len(date_components)

    if num_components == 1:
        date_string = date_string + '-00-00'
    elif num_components == 2:
        date_string = date_string + '-00'
    else:
        pass
    return date_string


def get_album_details(album_id):
    response = requests.get(f'https://vgmdb.info/album/{album_id}')
    if response.status_code == 200:
        return response.json()
    else:
        return None


def getBest(obj, orig='NA'):
    for lang in languages:
        if lang in obj:
            return obj[lang]
    return orig


def getTrackData(data):
    trackData = {}
    discNumber = 1
    for disc in data['discs']:
        trackData[discNumber] = {}
        trackNumber = 1
        for track in disc['tracks']:
            trackData[discNumber][trackNumber] = getBest(track['names'])
            trackNumber += 1
        discNumber += 1
    return trackData


def hasCoverOfType(audio, typ):
    for picture in audio.pictures:
        if picture.type == typ:
            return True
    return False

# get the count of tracks -> checks if the input is something like 4/20 -> truncates to 4


def getCount(discNo):
    if '/' in discNo:
        discNo = discNo.split('/')[0]
    if ':' in discNo:
        discNo = discNo.split('/')[0]
    return int(discNo)

########################## Helper Functions ############################


folder_path = "/run/media/arpit/DATA/OSTs/Visual Novels/07th Expansion/01 - Higurashi/04 - Anime, Movies, TV/8. Higurashi Sotsu/[2021.11.26] [KAXA-8151CD] When They Cry-Sotsu Original Soundtrack CD - Kenji Kawai"
album_id = 112318


# flags
PICS = False
ARRANGERS = False
COMPOSERS = False
ORGANIZATIONS = True
PERFORMERS = False
LYRICISTS = False
DATE = True
CATALOG = True
BARCODE = True


def tag_files(folderPath, album_id):
    print('Started...')
    try:
        data = get_album_details(album_id)
        if data is None:
            print('Failed, Please Try Again.')
            return
    except Exception as e:
        print('Failed, Please Try Again.')
        print(e)
        return
    trackData = getTrackData(data)
    if(PICS and 'picture_full' in data):
        response = requests.get(data['picture_full'])
        image_data = response.content
        picture = mutagen.flac.Picture()
        picture.data = image_data
        picture.type = 3
        picture.mime = 'image/jpeg'

    print(f'Album - {getBest(data["names"])} OK? (y/n)')
    resp = input()
    if resp not in 'yY':
        print("Closing")
        return

    for root, dirs, files in os.walk(folderPath):
        for file in files:
            if not file.endswith('.flac'):
                continue
            try:
                filePath = os.path.join(root, file)
                audio = FLAC(filePath)
                # Tagging Album specific Details
                audio['album'] = getBest(data['names'])

                if DATE and 'release_date' in data:
                    audio['date'] = standardize_date(data['release_date'])

                if CATALOG and 'catalog' in data:
                    audio['catalog'] = data['catalog']

                if BARCODE and 'barcode' in data:
                    audio['barcode'] = data['barcode']

                if(PICS and 'picture_full' in data and not hasCoverOfType(audio, 3)):
                    audio.add_picture(picture)

                if 'organizations' in data and ORGANIZATIONS:
                    for org in data['organizations']:
                        audio[org['role']] = getBest(org['names'])

                if 'lyricists' in data and LYRICISTS:
                    temp = []
                    for lyr in data['lyricists']:
                        temp.append(getBest(lyr['names']))
                    audio['lyricist'] = temp

                if 'performers' in data and PERFORMERS:
                    temp = []
                    for per in data['performers']:
                        temp.append(getBest(per['names']))
                    audio['performer'] = temp

                if 'arrangers' in data and ARRANGERS:
                    temp = []
                    for arr in data['arrangers']:
                        temp.append(getBest(arr['names']))
                    audio['arranger'] = temp

                if 'composers' in data and COMPOSERS:
                    temp = []
                    for comp in data['composers']:
                        temp.append(getBest(comp['names']))
                    audio['composer'] = temp

                # Tagging track specific details
                discNo = 1
                trackNo = 1
                try:
                    discNo = getCount(audio['discnumber'][0])
                except Exception as e:
                    print(e)
                try:
                    trackNo = getCount(audio['tracknumber'][0])
                except Exception as e:
                    # exception not allowed in TrackNumber
                    print(e)
                    return

                trackTitle = trackData[discNo][trackNo]
                totalTracks = len(trackData[discNo])
                totalDisks = len(trackData)
                tracksUpperBound = int(math.ceil(math.log10(totalTracks+1)))
                disksUpperBound = int(math.ceil(math.log10(totalDisks+1)))

                audio['tracknumber'] = str(trackNo).zfill(tracksUpperBound)
                audio['tracktotal'] = str(totalTracks)
                audio['discnumber'] = str(discNo).zfill(disksUpperBound)
                audio['disctotal'] = str(totalDisks)
                audio['title'] = trackTitle

                print(f'Done with file : {file} -> {trackNo}. {trackTitle}')
                audio.save()

            except Exception as e:
                print(e)


tag_files(folder_path, album_id)
