import os
import requests

from tabulate import tabulate
import urllib.request

from Modules.flagsAndSettings import *
from Modules.mutagenWrapper import AudioFactory


def Request(url):
    countLeft = APICALLRETRIES
    while countLeft > 0:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            pass
        countLeft -= 1
    return None


def getAlbumDetails(albumID):
    return Request(f'https://vgmdb.info/album/{albumID}')


def searchAlbum(albumName):
    return Request(f'https://vgmdb.info/search?q={albumName}')


def getBest(languageObject, languageOrder):
    for currentLanguage in languageOrder:
        for languageKey in languages[currentLanguage]:
            if languageKey in languageObject:
                return languageObject[languageKey]
    return list(languageObject.items())[0][0]


def getCount(discNumber):
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 4
    if '/' in discNumber:
        discNumber = discNumber.split('/')[0]
    elif ':' in discNumber:
        discNumber = discNumber.split(':')[0]
    return int(discNumber)


def getOneAudioFile(folderPath):
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() in supportedExtensions:
                return os.path.join(root, file)
    return None


def getAlbumName(folderPath: str):
    filePath = getOneAudioFile(folderPath)
    if filePath is None:
        print('No Audio File Present in the directory to get album name, please provide custom search term!')
        return None

    audio = AudioFactory.buildAudioManager(filePath)
    albumName = audio.getAlbum()
    if albumName is None:
        print('Audio file does not have an <album> tag!, please provide custom search term')
        return None
    return albumName


def yesNoUserInput():
    print('Continue? (Y/n) : ', end='')
    resp = input()
    if resp == 'n' or resp == 'N':
        return False
    return True


def noYesUserInput():
    print('Continue? (y/N) : ', end='')
    resp = input()
    if resp == 'y' or resp == 'Y':
        return True
    return False


def getAlbumTrackData(data, languageOrder):
    trackData = {}
    discNumber = 1
    for disc in data['discs']:
        trackData[discNumber] = {}
        trackNumber = 1
        for track in disc['tracks']:
            trackData[discNumber][trackNumber] = getBest(track['names'], languageOrder)
            trackNumber += 1
        discNumber += 1
    return trackData


def getFolderTrackData(folderPath):
    folderTrackData = {}
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension.lower() not in supportedExtensions:
                continue
            filePath = os.path.join(root, file)
            audio = AudioFactory.buildAudioManager(filePath)
            discNumber = 1
            trackNumber = 1
            discNumber = audio.getDiscNumber()
            if discNumber is not None:
                discNumber = getCount(discNumber)
            else:
                print(f'Disc Number not Present in file : {file}, Taking Default Value = 01')
                discNumber = 1

            trackNumber = audio.getTrackNumber()
            if trackNumber is not None:
                trackNumber = getCount(trackNumber)
            else:
                print(f'TrackNumber not Present in file : {file}, Skipped!')
                continue

            if discNumber not in folderTrackData:
                folderTrackData[discNumber] = {}
            if trackNumber in folderTrackData[discNumber]:
                print(
                    f'disc {discNumber}, Track {trackNumber} - {os.path.basename(folderTrackData[discNumber][trackNumber])} Conflicts with {file}')
                continue

            folderTrackData[discNumber][trackNumber] = filePath
    return folderTrackData


def doTracksAlign(albumTrackData, folderTrackData):
    flag = True
    tableData = []
    for discNumber, tracks in albumTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                tableData.append((discNumber, trackNumber, trackTitle, ''))
                flag = False
            else:
                tableData.append((discNumber, trackNumber, trackTitle, os.path.basename(
                    folderTrackData[discNumber][trackNumber])))

    for discNumber, tracks in folderTrackData.items():
        for trackNumber, trackTitle in tracks.items():
            if discNumber not in albumTrackData or trackNumber not in albumTrackData[discNumber]:
                tableData.append(
                    (discNumber, trackNumber, '', os.path.basename(
                        folderTrackData[discNumber][trackNumber])))
                flag = False

    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Title', 'fileName'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=53, tablefmt=tableFormat), end='\n\n')
    return flag


def downloadPicture(URL, path, name=None):
    try:
        pictureName = os.path.basename(URL)
        imagePath = os.path.join(path, pictureName)
        originalURLName, extension = os.path.splitext(imagePath)
        if name:
            finalImageName = name+extension
            if os.path.exists(os.path.join(path, finalImageName)):
                print(f'FileExists : {finalImageName}')
                return
        urllib.request.urlretrieve(URL, imagePath)
        if name is not None:
            originalURLName = name
            os.rename(imagePath, os.path.join(path, originalURLName+extension))
        print(f'Downloaded : {originalURLName}{extension}')
    except Exception as e:
        print(e)


def cleanName(name: str):
    forbiddenCharacters = {
        '<': 'ᐸ',
        '>': 'ᐳ',
        ':': '꞉',
        '"': 'ˮ',
        '\'': 'ʻ',
        '/': '／',
        '\\': '∖',
        '|': 'ǀ',
        '?': 'ʔ',
        '*': '∗',
        '+': '᛭',
        '%': '٪',
        '!': 'ⵑ',
        '`': '՝',
        '&': '&',  # keeping same as it is not forbidden, but it may cause problems
        '{': '❴',
        '}': '❵',
        '=': '᐀',
        # Not illegal, but the bigger version looks good (JK, it's kinda illegal, cd ~/Downloads :))
        '~': '～',
        '#': '#',  # couldn't find alternative
        '$': '$',  # couldn't find alternative
        '@': '@'  # couldn't find alternative
    }
    output = name
    for invalidCharacter, validAlternative in forbiddenCharacters.items():
        output = output.replace(invalidCharacter, validAlternative)
    return output


def fixDate(date):
    if date is None:
        return None
    date = date.strip()
    parts = date.split('-')
    parts += ['00'] * (3 - len(parts))
    normalized_date_str = '{}-{}-{}'.format(*parts)
    return normalized_date_str


def cleanSearchTerm(name):
    if name is None:
        return None

    def isJapanese(ch):
        return (ord(ch) >= 0x4E00 and ord(ch) <= 0x9FFF)

    def isChinese(ch):
        return (ord(ch) >= 0x3400 and ord(ch) <= 0x4DFF)

    ans = ""
    for ch in name:
        if ch.isalnum() or ch == ' ' or isJapanese(ch) or isChinese(ch):
            ans += ch
        else:
            ans += ' '
    return ans
