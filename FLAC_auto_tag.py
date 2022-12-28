import os
import json
import requests
import mutagen
from mutagen.flac import FLAC

################## Helper Functions ############################


def standardize_date(date_string: str) -> str:
    # Split the date string into its components
    date_components = date_string.split('-')
    num_components = len(date_components)

    # If the date string has only the year component, add placeholder values for the month and day
    if num_components == 1:
        date_string = date_string + '-00-00'
    # If the date string has the year and month components, add a placeholder value for the day
    elif num_components == 2:
        date_string = date_string + '-00'
    # Otherwise, the date string is already in the 'YYYY-MM-DD' format
    else:
        pass

    return date_string
################## Helper Functions ############################


languages = ['en', 'english', 'ja-latn', 'Romaji', 'ja', 'Japanese']
PICS = False
ARRANGERS = False
COMPOSERS = False
ORGANIZATIONS = True
PERFORMERS = False
LYRICISTS = False
DATE = True
CATALOG = True
BARCODE = True


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


def tag_files(folder_path, album_id):
    data = get_album_details(album_id)
    trackData = getTrackData(data)

    if(PICS and 'picture_full' in data):
        response = requests.get(data['picture_full'])
        image_data = response.content
        picture = mutagen.flac.Picture()
        picture.data = image_data
        picture.type = 3
        picture.mime = 'image/jpeg'

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if not file.endswith('.flac'):
                continue
            try:
                file_path = os.path.join(root, file)
                audio = FLAC(file_path)
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
                    temp  = []
                    for arr in data['arrangers']:
                        temp.append(getBest(arr['names']))
                    audio['arranger'] = temp
                
                if 'composers' in data and COMPOSERS:
                    temp = []
                    for comp in data['composers']:
                        temp.append(getBest(comp['names']))
                    audio['composer'] = temp

                # Tagging track specific details
                disc_no = 1
                track_no = 1
                try:
                    disc_no = int(audio['discnumber'][0])
                except Exception as e:
                    print(e)
                try:
                    track_no = int(audio['tracknumber'][0])
                except Exception as e:
                    print(e)

                audio['title'] = trackData[disc_no][track_no]

                audio.save()

            except Exception as e:
                print(e)


# folder_path = '/home/arpit/Programming/Python/[2021.11.26] [KAXA-8151CD] When They Cry-Sotsu Original Soundtrack CD - Kenji Kawai'
# album_id = 112318
folder_path = '/home/arpit/Programming/Python/[2005.12.22] [FCCT-0038] Anthology Drama CD Higurashi no Naku Koro ni Vol.1'
album_id = 19733
tag_files(folder_path, album_id)
