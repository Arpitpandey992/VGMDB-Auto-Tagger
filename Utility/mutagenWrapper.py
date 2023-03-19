# Importing abstract methods
from abc import ABC, abstractmethod

import os

from mutagen.flac import Picture as PictureFLAC, FLAC
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.id3._frames import APIC, TALB, TDRC, TRCK, COMM, TXXX, TPOS, TIT2
from mutagen.id3 import ID3

"""
This is a wrapper around mutagen module. This basically allows us to call the same functions for any extension, and hence reducing code complexity.
"""


def isString(var):
    return isinstance(var, str)


def splitAndGetFirst(discNumber):
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 4
    # output is a string, input can be an integer, float, ...
    if not isString(discNumber):
        return str(discNumber)

    if '/' in discNumber:
        discNumber = discNumber.split('/')[0]
    elif ':' in discNumber:
        discNumber = discNumber.split(':')[0]

    return discNumber


def splitAndGetSecond(discNumber):
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 20
    # output is a string, input can be an integer, float, ...
    if not isString(discNumber):
        return str(discNumber)

    if '/' in discNumber:
        discNumber = discNumber.split('/')
        if len(discNumber) < 2:
            return None
        discNumber = discNumber[1]
    elif ':' in discNumber:
        discNumber = discNumber.split(':')
        if len(discNumber) < 2:
            return None
        discNumber = discNumber[1]
    else:
        return None
    return discNumber


pictureNumberToName = {
    0: u'Other',
    1: u'File icon',
    2: u'Other file icon',
    3: u'Cover (front)',
    4: u'Cover (back)',
    5: u'Leaflet page',
    6: u'Media (e.g. lable side of CD)',
    7: u'Lead artist/lead performer/soloist',
    8: u'Artist/performer',
    9: u'Conductor',
    10: u'Band/Orchestra',
    11: u'Composer',
    12: u'Lyricist/text writer',
    13: u'Recording Location',
    14: u'During recording',
    15: u'During performance',
}

# Interface Class specifying the required functionality


def getFirstElement(listVariable):
    if not listVariable:
        return None
    return listVariable[0]


class IAudioManager(ABC):
    @abstractmethod
    def setTitle(self, newTitle: list[str]):
        """ Set the title of track """

    @abstractmethod
    def setAlbum(self, newAlbum: list[str]):
        """ Set the album name of the track """

    @abstractmethod
    def setDiscNumbers(self, discNumber: str, totalDiscs: str):
        """
        set disc number and total number of discs
        The arguments are supposed to be a string here
        """

    @abstractmethod
    def setTrackNumbers(self, trackNumber: str, totalTracks: str):
        """
        Set Track number and total number of tracks
        The arguments are supposed to be a string here
        """

    @abstractmethod
    def setComment(self, trackNumber: str):
        """ Set a comment """

    @abstractmethod
    def setPictureOfType(self, imageData, pictureType: int):
        """ Set a picture of some type (3 = front Cover) """

    @abstractmethod
    def hasPictureOfType(self, pictureType: int):
        """ Set a picture of some type (3 = front Cover) """

    @abstractmethod
    def deletePictureOfType(self, pictureType: int):
        """ Set a picture of some type (3 = front Cover) """

    @abstractmethod
    def setDate(self, date: str):
        """ Set the album release date """

    @abstractmethod
    def setCatalog(self, value: str):
        """ Set a custom tag as Key = value """

    @abstractmethod
    def setCustomTag(self, key: str, value: str | list[str]):
        """ Set a custom tag as Key = value """

    @abstractmethod
    def setDiscName(self, value: str):
        """ Set The Name of The Disc """

    @abstractmethod
    def getTitle(self) -> str:
        """ get the title of track """

    @abstractmethod
    def getAlbum(self) -> str:
        """ get the album name of the track """

    @abstractmethod
    def getArtist(self) -> str:
        """ get the album name of the track """

    @abstractmethod
    def getAlbumArtist(self) -> str:
        """ get the album Artist name of the track """

    @abstractmethod
    def getDiscNumber(self) -> str:
        """ get disc number and total number of discs """

    @abstractmethod
    def getTotalDiscs(self) -> str:
        """ get disc number and total number of discs """

    @abstractmethod
    def getTrackNumber(self) -> str:
        """ get Track number and total number of tracks """

    @abstractmethod
    def getTotalTracks(self) -> str:
        """ get Track number and total number of tracks """

    @abstractmethod
    def getComment(self) -> str:
        """ get a comment """

    @abstractmethod
    def getDate(self) -> str:
        """ get the album release date """

    @abstractmethod
    def getCustomTag(self, key: str) -> str:
        """ get a custom tag as Key = value """

    @abstractmethod
    def getCatalog(self) -> str:
        """ get Catalog Value """

    @abstractmethod
    def getDiscName(self) -> str:
        """ get the name of the disc """

    @abstractmethod
    def save(self):
        """ Apply metadata changes """

    @abstractmethod
    def getInformation(self):
        """ See the metadata information in Human Readable Format """

    @abstractmethod
    def addMultipleValues(self, key: str, listOfValues: list):
        """ Add multiple values to a particular tag """


class Vorbis(IAudioManager):
    def __init__(self, mutagen_object, extension):
        self.extension = extension.lower()
        self.audio = mutagen_object

    def setTitle(self, newTitle):
        self.audio['title'] = newTitle

    def setAlbum(self, newAlbum):
        self.audio['album'] = newAlbum

    def setDiscNumbers(self, discNumber, totalDiscs):
        self.audio['discnumber'] = discNumber
        self.audio['totaldiscs'] = totalDiscs
        self.audio['disctotal'] = totalDiscs

    def setTrackNumbers(self, trackNumber, totalTracks):
        self.audio['tracknumber'] = trackNumber
        self.audio['totaltracks'] = totalTracks
        self.audio['tracktotal'] = totalTracks

    def setComment(self, comment):
        self.audio['comment'] = comment

    def setPictureOfType(self, imageData, pictureType):
        import base64
        picture = PictureFLAC()
        picture.data = imageData
        picture.type = pictureType
        picture.mime = 'image/jpeg'
        picture.desc = pictureNumberToName[pictureType]
        if 'flac' in self.extension:
            self.audio.add_picture(picture)
        elif 'ogg' in self.extension:
            self.audio["metadata_block_picture"] = base64.b64encode(picture.write()).decode("ascii")

    def hasPictureOfType(self, pictureType):
        if 'ogg' in self.extension and "metadata_block_picture" in self.audio:
            return True
        elif 'flac' in self.extension:
            for picture in self.audio.pictures:
                if picture.type == pictureType:
                    return True
        return False

    def deletePictureOfType(self, pictureType):
        # This will remove all pictures sadly,
        # i couldn't find any proper method to remove only one picture
        if 'flac' in self.extension:
            self.audio.clear_pictures()
        elif 'ogg' in self.extension and "metadata_block_picture" in self.audio:
            self.audio.pop("metadata_block_picture")

    def setDate(self, date):
        self.audio['date'] = date

    def setCustomTag(self, key, value):
        self.audio[key] = value

    def setCatalog(self, value: str):
        self.setCustomTag('CATALOGNUMBER', value)
        self.setCustomTag('CATALOG', value)

    def setDiscName(self, value: str):
        self.setCustomTag('DISCSUBTITLE', value)

    def getTitle(self):
        ans = self.audio.get('title')
        return getFirstElement(ans)

    def getAlbum(self):
        ans = self.audio.get('album')
        return getFirstElement(ans)

    def getArtist(self):
        ans = self.audio.get('artist')
        return getFirstElement(ans)

    def getAlbumArtist(self):
        ans = self.audio.get('albumartist')
        return getFirstElement(ans)

    def getDiscNumber(self):
        ans = self.audio.get('discnumber')
        return getFirstElement(ans)

    def getTotalDiscs(self):
        ans = self.audio.get('disctotal')
        if ans is None:
            ans = self.audio.get('totaldiscs')
        return getFirstElement(ans)

    def getTrackNumber(self):
        ans = self.audio.get('tracknumber')
        return getFirstElement(ans)

    def getTotalTracks(self):
        ans = self.audio.get('tracktotal')
        if ans is None:
            ans = self.audio.get('totaltracks')
        return getFirstElement(ans)

    def getComment(self):
        ans = self.audio.get('comment')
        return getFirstElement(ans)

    def getDate(self):
        possibleFields = ['date', 'ORIGINALDATE', 'year', 'ORIGINALYEAR']
        for field in possibleFields:
            ans = getFirstElement(self.audio.get(field))
            if ans:
                return ans
        return None

    def getCustomTag(self, key):
        ans = self.audio.get(key)
        return getFirstElement(ans)

    def getCatalog(self):
        possibleFields = ['CATALOGNUMBER', 'CATALOG', 'LABELNO']
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:
                return ans
        return None

    def getDiscName(self):
        possibleFields = ['DISCSUBTITLE', 'DISCNAME']
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:
                return ans
        return None

    def save(self):
        self.audio.save()

    def getInformation(self):
        return self.audio.pprint()

    def addMultipleValues(self, key: str, listOfValues: list):
        self.audio[key] = listOfValues


class ID_3(IAudioManager):
    """
    mainly for mp3 files -> full functionality
    for wav files -> only getting tags is functional currently, cannot set tags
    """

    def __init__(self, mutagen_object, extension):
        self.audio = mutagen_object
        self.extension = extension.lower()

    def setTitle(self, newTitle):
        self.audio.add(TIT2(encoding=3, text=[newTitle[0]]))
        if len(newTitle) > 1:
            # Multiple titles are not supported in ID3 -> add other titles as custom tag!
            self.addMultipleValues("Alternate Title", newTitle[1:])

    def setAlbum(self, newAlbum):
        self.audio.add(TALB(encoding=3, text=[newAlbum[0]]))
        if len(newAlbum) > 1:
            # Multiple titles are not supported in ID3 -> add other titles as custom tag!
            self.addMultipleValues("Alternate Album Name", newAlbum[1:])

    def setDiscNumbers(self, discNumber, totalDiscs):
        self.audio.add(TPOS(
            encoding=3,
            text=[discNumber + '/' + totalDiscs]
        ))

    def setTrackNumbers(self, trackNumber, totalTracks):
        self.audio.add(TRCK(
            encoding=3,
            text=[trackNumber + '/' + totalTracks]
        ))

    def setComment(self, comment):
        self.audio.add(COMM(encoding=3, text=[comment]))

    def setPictureOfType(self, imageData, pictureType):
        picture = APIC(encoding=3,
                       mime='image/jpeg',
                       type=pictureType,
                       desc=pictureNumberToName[pictureType],
                       data=imageData)
        self.audio.add(picture)

    def hasPictureOfType(self, pictureType):
        if self.extension == '.wav':
            for tag in self.audio.tags:
                if tag.startswith("APIC:"):
                    frame = self.audio.get(tag)
                    if frame.type == pictureType:
                        return True

        elif self.extension == '.mp3':
            pictures = self.audio.getall("APIC:")
            if pictures:
                for picture in pictures:
                    if picture.type == pictureType:
                        return True
        return False

    def deletePictureOfType(self, pictureType):
        if self.extension == '.wav':
            for tag in self.audio.tags:
                if tag.startswith("APIC:"):
                    frame = self.audio.get(tag)
                    if frame.type == pictureType:
                        self.audio.pop(frame.HashKey)
        elif self.extension == '.mp3':
            for frame in self.audio.getall("APIC:"):
                if frame.type == pictureType:
                    self.audio.pop(frame.HashKey)

    def setDate(self, date):
        self.audio.add(TDRC(encoding=3, text=[date]))

    def setCustomTag(self, key, value):
        self.audio.add(TXXX(encoding=3, desc=key, text=[value]))

    def setCatalog(self, value: str):
        self.setCustomTag('CATALOGNUMBER', value)
        self.setCustomTag('CATALOG', value)

    def setDiscName(self, value: str):
        self.setCustomTag('DISCSUBTITLE', value)

    def getTitle(self):
        ans = self.audio.get('TIT2')
        return getFirstElement(ans.text) if ans else None

    def getAlbum(self):
        ans = self.audio.get('TALB')
        return getFirstElement(ans.text) if ans else None

    def getArtist(self):
        ans = self.audio.get('TPE1')
        return getFirstElement(ans)

    def getAlbumArtist(self):
        ans = self.audio.get('TPE2')
        return getFirstElement(ans.text) if ans else None

    def getDiscNumber(self):
        ans = self.audio.get('TPOS')
        return splitAndGetFirst(getFirstElement(ans.text)) if ans else None

    def getTotalDiscs(self):
        ans = self.audio.get('TPOS')
        return splitAndGetSecond(getFirstElement(ans.text)) if ans else None

    def getTrackNumber(self):
        ans = self.audio.get('TRCK')
        return splitAndGetFirst(getFirstElement(ans.text)) if ans else None

    def getTotalTracks(self):
        ans = self.audio.get('TRCK')
        return splitAndGetSecond(getFirstElement(ans.text)) if ans else None

    def getComment(self):
        ans = self.audio.get('COMM')
        return getFirstElement(ans.text) if ans else None

    def getDate(self):
        ans = self.audio.get('TDRC')
        if not ans or not ans.text:
            return None
        ans = getFirstElement(ans.text)
        if not ans or not ans.text:
            return None
        return ans.text

    def getCustomTag(self, key):
        if self.extension == '.mp3':
            frames = self.audio.getall("TXXX")
            for frame in frames:
                if key in frame.HashKey:
                    return frame.text[0]
        elif self.extension == '.wav':
            tags = self.audio.tags
            for tag in tags:
                if not tag.startswith("TXXX") or key not in tag:
                    continue
                return self.audio.get(tag).text[0]
        return None

    def getCatalog(self):
        possibleFields = ['CATALOGNUMBER', 'CATALOG', 'LABELNO']
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:
                return ans
        return None

    def getDiscName(self):
        possibleFields = ['DISCSUBTITLE', 'DISCNAME']
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:
                return ans
        return None

    def save(self):
        self.audio.save()

    def getInformation(self):
        return self.audio.pprint()

    def addMultipleValues(self, key: str, listOfValues: list[str]):
        self.audio.add(TXXX(encoding=3, desc=key, text=listOfValues))


audioFileHandler = {
    '.flac': [Vorbis, FLAC],
    '.wav': [ID_3, WAVE],
    '.mp3': [ID_3, ID3],
    '.ogg': [Vorbis, OggVorbis],
    '.opus': [Vorbis, OggOpus],
}
supportedExtensions = audioFileHandler.keys()


class AudioFactory():
    @staticmethod
    def buildAudioManager(filePath) -> IAudioManager:

        _, extension = os.path.splitext(filePath)
        codec = audioFileHandler[extension.lower()][0]
        handler = audioFileHandler[extension.lower()][1]
        return codec(handler(filePath), extension)


if __name__ == '__main__':
    filePath = "/run/media/arpit/DATA/Music/Anime/Mo Dao Zu Shi (Grandmaster of Demonic Cultivation) (魔道祖师)/Original Soundtrack [Spotify-320Kbps OGG]/01 - Various Artists - 醉梦前尘.ogg"
    audio = AudioFactory.buildAudioManager(filePath)
    print(audio.getDate())
