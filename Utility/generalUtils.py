import os
import sys
from typing import Union, Optional, Any
import requests
from math import ceil, log10
import urllib.request
from Imports.flagsAndSettings import APICALLRETRIES, languages
from Types.search import SearchAlbum
from Types.albumData import AlbumData, TrackData


def Request(url: str) -> Optional[dict[Any, Any]]:
    countLeft = APICALLRETRIES
    while countLeft > 0:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        countLeft -= 1
    return None


def getAlbumDetails(albumID: str) -> AlbumData:
    return Request(f'https://vgmdb.info/album/{albumID}')  # type: ignore


def searchAlbum(albumName: str) -> Optional[list[SearchAlbum]]:
    searchResult = Request(f'https://vgmdb.info/search?q={albumName}')
    if not searchResult:
        return None
    return searchResult['results']['albums']


def getBest(languageObject: dict[str, str], languageOrder: list[str]) -> str:
    for currentLanguage in languageOrder:
        for languageKey in languages[currentLanguage]:
            if languageKey in languageObject:
                return languageObject[languageKey]
    return list(languageObject.items())[0][1]


def getProperCount(count: Union[str, int], totalCount: Union[str, int]) -> str:
    # if total tracks = 100, then this function will convert 1 to 001 for consistent sorting
    try:
        upperBound = int(ceil(log10(int(totalCount) + 1)))
        return str(count).zfill(upperBound)

    except Exception:
        print(Exception)

    return str(count)


def yesNoUserInput() -> bool:
    print('Continue? (Y/n) : ', end='')
    resp = input()
    if resp == 'n' or resp == 'N':
        return False
    return True


def noYesUserInput() -> bool:
    print('Continue? (y/N) : ', end='')
    resp = input()
    if resp == 'y' or resp == 'Y':
        return True
    return False


def downloadPicture(URL: str, path: str, name=None):
    try:
        pictureName = os.path.basename(URL)
        imagePath = os.path.join(path, pictureName)
        originalURLName, extension = os.path.splitext(imagePath)
        if name:
            finalImageName = name + extension
            if os.path.exists(os.path.join(path, finalImageName)):
                print(f'FileExists : {finalImageName}')
                return
        urllib.request.urlretrieve(URL, imagePath)
        if name is not None:
            originalURLName = name
            os.rename(imagePath, os.path.join(path, originalURLName + extension))
        print(f'Downloaded : {originalURLName}{extension}')
    except Exception as e:
        print(e)


forbiddenCharacters = {
    '<': 'ᐸ',
    '>': 'ᐳ',
    ':': '꞉',
    '"': 'ˮ',
    '\'': 'ʻ',
    # '/': '／', # Looks far too stretched, but is more popular for some reason
    '/': 'Ⳇ',  # This one looks more natural
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
    # '~': '～',  # Not using this because it could be present in catalog number as well, may cause problems though
    '#': '#',  # couldn't find alternative
    '$': '$',  # couldn't find alternative
    '@': '@'  # couldn't find alternative
}


def cleanName(name: str) -> str:
    output = name
    for invalidCharacter, validAlternative in forbiddenCharacters.items():
        output = output.replace(invalidCharacter, validAlternative)
    return output


def fixDate(date: Optional[str]) -> Optional[str]:
    """
    Makes sure that date is in the form YYYY-MM-DD
    fills unknows fields with 00
    """
    if not date:
        return date
    date = date.strip()
    parts = date.split('-')
    parts += ['00'] * (3 - len(parts))
    normalized_date_str = '{}-{}-{}'.format(*parts)
    return normalized_date_str


def cleanSearchTerm(name: Optional[str]) -> Optional[str]:
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


def updateDict(dictionary: Union[dict, TrackData, AlbumData], keyValuePairs: dict) -> None:
    """In place update some keys present in a dictionary"""
    for key, value in keyValuePairs.items():
        dictionary[key] = value


def printAndMoveBack(text: str):
    sys.stdout.write("\033[K")  # Clear to the end of line
    print(text, end='\r')
    sys.stdout.flush()

def isLanguagePresent(languageObject: dict[str, str], language: str) -> bool:
    presentLanguages = [key.lower().strip() for key in languageObject]
    if language in languages:
        for languageSynonym in languages[language]:
            if languageSynonym.lower().strip() in presentLanguages:
                return True
    return False
