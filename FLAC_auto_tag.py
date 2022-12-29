import os
import json
import requests
import math
import mutagen
from mutagen.flac import FLAC
import argparse
import shutil


# languages to be probed from VGMDB in the given order of priority
languages = ['en', 'English', 'ja-latn', 'Romaji', 'ja', 'Japanese']
BACKUPFOLDER = 'D:\\backups'
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
    return Request(f'https://vgmdb.info/search/{albumName}')


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


# flags
PICS = True
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


def backupFolder(inputFolder):
    try:
        destinationFolder = BACKUPFOLDER
        print(f'Backing Up {inputFolder}...')
        backupFolder = os.path.join(
            destinationFolder, os.path.basename(inputFolder))
        shutil.copytree(inputFolder, backupFolder, dst_dir_exists_ok=True)
        print(f'Successfully copied {inputFolder} to {backupFolder}')

    except Exception as e:
        print(f'{inputFolder} Backup Failed, aborting Program')
        print(e)
        exit(0)


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

    if CONFIRM:
        print(f'Album - {getBest(data["names"])} OK? (y/n)')
        print(f'Link - {data["vgmdb_link"]}')
        resp = input()
        if resp not in 'yY':
            return False

    if BACKUP:
        backupFolder(folderPath)

    trackData = getTrackData(data)
    if(PICS and 'picture_full' in data):
        response = requests.get(data['picture_full'])
        image_data = response.content
        picture = mutagen.flac.Picture()
        picture.data = image_data
        picture.type = 3
        picture.mime = 'image/jpeg'

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

                # if 'lyricists' in data and LYRICISTS:
                #     temp = []
                #     for lyr in data['lyricists']:
                #         temp.append(getBest(lyr['names']))
                #     audio['lyricist'] = temp

                # if 'performers' in data and PERFORMERS:
                #     temp = []
                #     for per in data['performers']:
                #         temp.append(getBest(per['names']))
                #     audio['performer'] = temp

                # if 'arrangers' in data and ARRANGERS:
                #     temp = []
                #     for arr in data['arrangers']:
                #         temp.append(getBest(arr['names']))
                #     audio['arranger'] = temp

                # if 'composers' in data and COMPOSERS:
                #     temp = []
                #     for comp in data['composers']:
                #         temp.append(getBest(comp['names']))
                #     audio['composer'] = temp

                # Tagging track specific details
                discNo = 1
                trackNo = 1
                try:
                    discNo = getCount(audio['discnumber'][0])
                except Exception as e:
                    print(
                        f'DiscNumber not Present in file {file}, Taking Default Value = 01')
                try:
                    trackNo = getCount(audio['tracknumber'][0])
                except Exception as e:
                    # exception not allowed in TrackNumber
                    print(f'TrackNumber not Present in file {file}, Skipped!')
                    continue

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

                print(
                    f'--> Done with file : {file} -> {trackNo}. {trackTitle}')
                audio.save()

            except Exception as e:
                print(e)
    return True


def getOneFlacFile(folderPath):
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            if file.endswith('.flac'):
                return os.path.join(root, file)
    return None


def findAndTagAlbum(folderPath):

    filePath = getOneFlacFile(folderPath)
    if filePath is None:
        print('No Flac File Present in the directory')
        return None

    flac = FLAC(filePath)
    if 'album' not in flac or not flac['album']:
        return None
    albumName = flac.get("album")[0]

    data = searchAlbum(albumName)
    if data is None or not data['results']['albums']:
        return None
    for album in data['results']['albums']:
        albumID = album['link'].split('/')[1]
        if tag_files(folderPath, albumID):
            return True
    return False


folderPath = r"D:\OSTs\Visual Novels\07th Expansion\02 - Umineko\02 - Visual Novel (Console)\[2012.01.25] [YZPB-5001] Inanna no Mita Yume - Zwei"

parser = argparse.ArgumentParser(description='Check and Fix FLAC Files')
parser.add_argument('folderPath', nargs='?', help='Flac directory path')

args = parser.parse_args()
if args.folderPath:
    folderPath = args.folderPath

print('Started...')
if findAndTagAlbum(folderPath):
    print('Done Tagging')
else:
    print(f"Couldn't Tag the Album at {folderPath}")
