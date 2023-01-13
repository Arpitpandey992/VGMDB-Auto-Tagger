# Importing abstract methods
from abc import ABC, abstractmethod

import os

from mutagen.flac import Picture as PictureFLAC, FLAC
from mutagen.id3._frames import APIC, TALB, TDRC, TRCK, COMM, TXXX, TPOS, TIT2
from mutagen.id3 import ID3


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


class IAudioManager(ABC):
    @abstractmethod
    def setTitle(self, newTitle: str):
        """ Set the title of track """

    @abstractmethod
    def setAlbum(self, newAlbum: str):
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
    def setCustomTag(self, key: str, value: str):
        """ Set a custom tag as Key = value """

    def getTitle(self):
        """ get the title of track """

    @abstractmethod
    def getAlbum(self):
        """ get the album name of the track """

    @abstractmethod
    def getDiscNumber(self):
        """ get disc number and total number of discs """

    def getTotalDiscs(self):
        """ get disc number and total number of discs """

    @abstractmethod
    def getTrackNumber(self):
        """ get Track number and total number of tracks """

    def getTotalTracks(self):
        """ get Track number and total number of tracks """

    @abstractmethod
    def getComment(self):
        """ get a comment """

    @abstractmethod
    def getDate(self):
        """ get the album release date """

    @abstractmethod
    def getCustomTag(self, key: str):
        """ get a custom tag as Key = value """

    @abstractmethod
    def save(self):
        """ Apply metadata changes """

    @abstractmethod
    def getInformation(self):
        """ See the metadata information in Human Readable Format """

    @abstractmethod
    def addMultipleValues(self, key: str, listOfValues: list):
        """ Add multiple values to a particular tag """


class Flac(IAudioManager):
    def __init__(self, filePath):
        self.audio = FLAC(filePath)

    def setTitle(self, newTitle):
        self.audio['title'] = newTitle

    def setAlbum(self, newAlbum):
        self.audio['album'] = newAlbum

    def setDiscNumbers(self, discNumber, totalDiscs):
        self.audio['discnumber'] = discNumber
        self.audio['disctotal'] = totalDiscs

    def setTrackNumbers(self, trackNumber, totalTracks):
        self.audio['tracknumber'] = trackNumber
        self.audio['tracktotal'] = totalTracks

    def setComment(self, comment):
        self.audio['comment'] = comment

    def setPictureOfType(self, imageData, pictureType):
        picture = PictureFLAC()
        picture.data = imageData
        picture.type = pictureType
        picture.mime = 'image/jpeg'
        picture.desc = pictureNumberToName[pictureType]
        self.audio.add_picture(picture)

    def hasPictureOfType(self, pictureType):
        for picture in self.audio.pictures:
            if picture.type == pictureType:
                return True
        return False

    def deletePictureOfType(self, pictureType):
        # This will remove all pictures sadly,
        # i couldn't find any proper method to remove only one picture
        self.audio.clear_pictures()

    def setDate(self, date):
        self.audio['date'] = date

    def setCustomTag(self, key, value):
        self.audio[key] = value

    def getTitle(self):
        ans = self.audio.get('title')
        return ans[0] if ans is not None else None

    def getAlbum(self):
        ans = self.audio.get('album')
        return ans[0] if ans is not None else None

    def getDiscNumber(self):
        ans = self.audio.get('discnumber')
        return ans[0] if ans is not None else None

    def getTotalDiscs(self):
        ans = self.audio.get('disctotal')
        return ans[0] if ans is not None else None

    def getTrackNumber(self):
        ans = self.audio.get('tracknumber')
        return ans[0] if ans is not None else None

    def getTotalTracks(self):
        ans = self.audio.get('tracktotal')
        return ans[0] if ans is not None else None

    def getComment(self):
        ans = self.audio.get('comment')
        return ans[0] if ans is not None else None

    def getDate(self):
        ans = self.audio.get('date')
        return ans[0] if ans is not None else None

    def getCustomTag(self, key):
        ans = self.audio.get(key)
        return ans[0] if ans is not None else None

    def save(self):
        self.audio.save()

    def getInformation(self):
        return self.audio.pprint()

    def addMultipleValues(self, key: str, listOfValues: list):
        self.audio[key] = listOfValues


class Mp3(IAudioManager):
    def __init__(self, filePath):
        self.audio = ID3(filePath)

    def setTitle(self, newTitle):
        self.audio.add(TIT2(encoding=3, text=[newTitle]))

    def setAlbum(self, newAlbum):
        self.audio.add(TALB(encoding=3, text=[newAlbum]))

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
        pictures = self.audio.getall("APIC")
        if pictures:
            for picture in pictures:
                if picture.type == pictureType:
                    return True
        return False

    def deletePictureOfType(self, pictureType):
        for frame in self.audio.getall("APIC:"):
            if frame.type == pictureType:
                self.audio.pop(frame.HashKey)

    def setDate(self, date):
        self.audio.add(TDRC(encoding=3, text=[date]))

    def setCustomTag(self, key, value):
        self.audio.add(TXXX(encoding=3, desc=key, text=[value]))

    def getTitle(self):
        ans = self.audio.get('TIT2')
        return ans.text[0] if ans else None

    def getAlbum(self):
        ans =  self.audio.get('TALB')
        return ans.text[0] if ans else None

    def getDiscNumber(self):
        ans =  self.audio.get('TPOS')
        return ans.text[0] if ans else None

    def getTotalDiscs(self):
        ans =  self.audio.get('TPOS')
        return ans.text[0] if ans else None

    def getTrackNumber(self):
        ans =  self.audio.get('TRCK')
        return ans.text[0] if ans else None

    def getTotalTracks(self):
        ans =  self.audio.get('TRCK')
        return ans.text[0] if ans else None

    def getComment(self):
        ans =  self.audio.get('COMM')
        return ans.text[0] if ans else None

    def getDate(self):
        ans =  self.audio.get('TDRC')
        return ans.text[0] if ans else None

    def getCustomTag(self, key):
        for frame in self.audio.getall("TXXX"):
            if key in frame.HashKey:
                return frame.text[0]
        return None
        # return self.audio.getall(key)[0].text

    def save(self):
        self.audio.save()

    def getInformation(self):
        return self.audio.pprint()

    def addMultipleValues(self, key: str, listOfValues: list):
        self.audio.add(TXXX(encoding=3, desc=key, text=listOfValues))


class AudioFactory():
    @staticmethod
    def buildAudioManager(filePath) -> IAudioManager:
        audioFileHandler = {
            '.flac': Flac,
            '.mp3': Mp3,
        }
        _, extension = os.path.splitext(filePath)
        return audioFileHandler[extension.lower()](filePath)