import os
import json
import requests
import math
import mutagen
from mutagen.flac import FLAC
import argparse
import shutil


# languages to be probed from VGMDB in the given order of priority
languages = ['ja-latn', 'Romaji', 'en', 'English',
             'English (Apple Music)', 'ja', 'Japanese']
BACKUPFOLDER = '/run/media/arpit/DATA/backups'
APICALLRETRIES = 5

################## Helper Functions ############################


def Request(url):
    countLeft = APICALLRETRIES
    while countLeft > 0:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(e)
        countLeft -= 1
    return None


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


def getAlbumDetails(albumID):
    return Request(f'https://vgmdb.info/album/{albumID}')


def searchAlbum(albumName):
    return Request(f'https://vgmdb.info/search?q={albumName}')


def getBest(obj, orig='NA'):
    for lang in languages:
        if lang in obj:
            return obj[lang]
    return orig


def hasCoverOfType(audio, typ):
    for picture in audio.pictures:
        if picture.type == typ:
            return True
    return False


def getCount(discNumber):
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 4
    if '/' in discNumber:
        discNumber = discNumber.split('/')[0]
    if ':' in discNumber:
        discNumber = discNumber.split('/')[0]
    return int(discNumber)


def getOneFlacFile(folderPath):
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            if file.endswith('.flac'):
                return os.path.join(root, file)
    return None


def yesNoUserInput():
    print('Continue? (y/n) : ', end='')
    resp = input()
    if resp not in 'yY':
        return False
    return True
    print('\n', end='')


def getAlbumTrackData(data):
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


def getFolderTrackData(folderPath):
    folderTrackData = {}
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            if not file.endswith('.flac'):
                continue

            filePath = os.path.join(root, file)
            audio = FLAC(filePath)
            discNumber = 1
            trackNumber = 1
            try:
                discNumber = getCount(audio['discnumber'][0])
            except Exception as e:
                print(
                    f'Disc Number not Present in file : {file}, Taking Default Value = 01')
            try:
                trackNumber = getCount(audio['tracknumber'][0])
            except Exception as e:
                print(
                    f'TrackNumber not Present in file : {file}, Skipped!')
                continue

            if discNumber not in folderTrackData:
                folderTrackData[discNumber] = {}
            if trackNumber in folderTrackData[discNumber]:
                print(
                    f'disc {discNumber}, Track {trackNumber} - {folderTrackData[discNumber][trackNumber]} Already Present')
                print(f'cannot add {file}')
                continue

            folderTrackData[discNumber][trackNumber] = filePath
    print('Done getting TrackData')
    return folderTrackData


def doTracksAlign(albumTrackData, folderTrackData):
    flag = True
    if len(albumTrackData) != len(folderTrackData):
        flag = False
    for discNumber, tracks in albumTrackData.items():
        if(discNumber not in folderTrackData or len(tracks) != len(folderTrackData[discNumber])):
            flag = False

    for discNumber, tracks in albumTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                print('{:<50s} {:<10s} {:<50s}'.format(
                    f'{discNumber}/{trackNumber}. {trackTitle}',
                    '->',
                    '**NOT AVAILABLE**'))
            else:
                print('{:<50s} {:<10s} {:<50s}'.format(
                    f'{discNumber}/{trackNumber}. {trackTitle}',
                    '->',
                    os.path.basename(folderTrackData[discNumber][trackNumber])))
    print('\n', end='')
    return flag


########################## Helper Functions ############################
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
# Very important to manually check and confirm if the album matches or not. Some automatic checks are there but manual checking should be done
CONFIRM = True
BACKUP = True


def tag_files(folderPath, albumID):
    try:
        data = getAlbumDetails(albumID)
        if data is None:
            print('Failed, Please Try Again.')
            return False
    except Exception as e:
        print('Failed, Please Try Again.')
        print(e)
        return False
    albumLink = data["vgmdb_link"]
    while albumLink and albumLink[-1] != '?':
        albumLink = albumLink[:-1]
    albumLink = albumLink[:-1]

    if CONFIRM:
        print(f'Link - {albumLink}')
        print(f'Album - {getBest(data["names"])}')
        if not yesNoUserInput():
            print('\n', end='')
            return False

    print('\n', end='')
    print('\n', end='')
    albumTrackData = getAlbumTrackData(data)
    folderTrackData = getFolderTrackData(folderPath)
    print('\n', end='')

    if not doTracksAlign(albumTrackData, folderTrackData):
        print('The tracks are not fully fitting the album data received from VGMDB!')
        if not yesNoUserInput():
            print('\n', end='')
            return False
    else:
        print('Tracks are perfectly aligning with the album data!')

    print('\n', end='')
    print('\n', end='')
    if BACKUP:
        try:
            destinationFolder = BACKUPFOLDER
            print(f'Backing Up {folderPath}...')
            print('\n', end='')
            backupFolder = os.path.join(
                destinationFolder, os.path.basename(folderPath))
            shutil.copytree(folderPath, backupFolder, dirs_exist_ok=False)
            print(f'Successfully copied {folderPath} to {backupFolder}')

        except Exception as e:
            print("Backup Couldn't Be Completed :(")
            print(e)
            if not yesNoUserInput():
                return False
    print('\n', end='')
    print('\n', end='')

    totalTracks = 0
    for disc in albumTrackData:
        totalTracks += len(albumTrackData[disc])
    totalDisks = len(albumTrackData)
    tracksUpperBound = int(math.ceil(math.log10(totalTracks+1)))
    disksUpperBound = int(math.ceil(math.log10(totalDisks+1)))
    albumName = getBest(data['names'])

    if(PICS and 'picture_full' in data):
        response = requests.get(data['picture_full'])
        image_data = response.content
        picture = mutagen.flac.Picture()
        picture.data = image_data
        picture.type = 3
        picture.mime = 'image/jpeg'

    for discNumber, tracks in albumTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                continue

            filePath = folderTrackData[discNumber][trackNumber]
            fileName = os.path.basename(filePath)
            audio = FLAC(filePath)

            # Tagging Album specific Details

            audio['album'] = albumName
            audio['tracktotal'] = str(totalTracks)
            audio['disctotal'] = str(totalDisks)
            audio['comment'] = f'Find the tracklist at {albumLink}'

            if DATE and 'release_date' in data:
                audio['date'] = standardize_date(data['release_date'])

            if CATALOG and 'catalog' in data:
                audio['catalog'] = data['catalog']

            if BARCODE and 'barcode' in data:
                audio['barcode'] = data['barcode']

            if(PICS and 'picture_full' in data and not hasCoverOfType(audio, 3)):
                audio.add_picture(picture)

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

            print('{:<10s} {:<50s} {:10s} {:<50s}'.format(
                'File Tagged : ',
                fileName,
                '->',
                f'{discNumber}/{trackNumber}. {trackTitle}'
            ))
            audio.save()

    print('\n', end='')
    print('\n', end='')
    return True


def findAndTagAlbum(folderPath):

    filePath = getOneFlacFile(folderPath)
    if filePath is None:
        print('No Flac File Present in the directory')
        print('\n', end='')
        print('\n', end='')
        return None

    flac = FLAC(filePath)
    if 'album' not in flac or not flac['album']:
        return None
    albumName = flac.get("album")[0]
    print(f'Searching for album : {albumName}')
    print('\n', end='')
    data = searchAlbum(albumName)
    if data is None or not data['results']['albums']:
        return None
    for album in data['results']['albums']:
        albumID = album['link'].split('/')[1]
        if tag_files(folderPath, albumID):
            return True
    return False


folderPath = "/run/media/arpit/DATA/OSTs/Anime/Fairy Tail/FAIRY TAIL ORIGINAL SOUND COLLECTION"
parser = argparse.ArgumentParser(description='Check and Fix FLAC Files')
parser.add_argument('folderPath', nargs='?', help='Flac directory path')
parser.add_argument('--ID', '-i', type=str, default=None,
                    help='Provide Album ID')
args = parser.parse_args()


print('Started...')
print('\n', end='')
print('\n', end='')
if folderPath[-1] == '/':
    folderPath = folderPath[:-1]
if args.folderPath:
    folderPath = args.folderPath
if args.ID is not None:
    if tag_files(folderPath, args.ID):
        print('Done Tagging')
    else:
        print(f"Couldn't Tag the Album at {folderPath}")
else:
    if findAndTagAlbum(folderPath):
        print('Done Tagging')
    else:
        print(f"Couldn't Tag the Album at {folderPath}")
