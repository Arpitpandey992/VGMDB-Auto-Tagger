# Importing abstract methods
from abc import ABC, abstractmethod

import os
from typing import Union, Optional, List, Any

from mutagen.flac import Picture as PictureFLAC, FLAC
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.id3._frames import APIC, TALB, TDRC, TRCK, COMM, TXXX, TPOS, TIT2
from mutagen.id3 import ID3
from mutagen.mp4 import MP4, MP4Cover

"""
This is a wrapper around mutagen module. This basically allows us to call the same functions for any extension, and hence reducing code complexity.
"""


def isString(var) -> bool:
    return isinstance(var, str)


def splitAndGetFirst(discNumber: Optional[str]) -> Optional[str]:
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 4
    # output is a string, input can be an integer, float, ...
    if not discNumber:
        return None
    if not isString(discNumber):
        return str(discNumber)

    if '/' in discNumber:
        discNumber = discNumber.split('/')[0]
    elif ':' in discNumber:
        discNumber = discNumber.split(':')[0]

    return discNumber


def splitAndGetSecond(discNumber: Optional[str]) -> Optional[str]:
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 20
    # output is a string, input can be an integer, float, ...
    if not discNumber:
        return None
    if not isString(discNumber):
        return str(discNumber)

    if '/' in discNumber:
        discNumberElements = discNumber.split('/')
        if len(discNumberElements) < 2:
            return None
        discNumber = discNumberElements[1]
    elif ':' in discNumber:
        discNumberElements = discNumber.split(':')
        if len(discNumberElements) < 2:
            return None
        discNumber = discNumberElements[1]
    else:
        return None
    return discNumber


def getFirstElement(listVariable: Optional[Union[List, Any]]) -> Any:
    if not listVariable:
        return None
    return listVariable[0]


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


"""
Interface Class for generalizing usage of Mutagen across multiple formats
"""


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
        """ Set comment """

    @abstractmethod
    def setPictureOfType(self, imageData: bytes, pictureType: int):
        """ Set a picture of some type (3 = front Cover) """

    @abstractmethod
    def hasPictureOfType(self, pictureType: int):
        """ check whether a picture of some type (3 = front Cover) is present"""

    @abstractmethod
    def deletePictureOfType(self, pictureType: int) -> bool:
        """ delete a picture of some type (3 = front Cover) """

    @abstractmethod
    def setDate(self, date: str):
        """ Set the album release date """

    @abstractmethod
    def setCatalog(self, value: str):
        """ Set Catalog number """

    @abstractmethod
    def setCustomTag(self, key: str, value: Union[str, List[str]]):
        """ Set a custom tag as Key = value """

    @abstractmethod
    def setDiscName(self, value: str):
        """ Set The Name of The Disc """

    @abstractmethod
    def getTitle(self) -> Optional[str]:
        """ get the title of track """

    @abstractmethod
    def getAlbum(self) -> Optional[str]:
        """ get the album name of the track """

    @abstractmethod
    def getArtist(self) -> Optional[str]:
        """ get the artist name of the track """

    @abstractmethod
    def getAlbumArtist(self) -> Optional[str]:
        """ get the album Artist name """

    @abstractmethod
    def getDiscNumber(self) -> Optional[str]:
        """ get disc number """

    @abstractmethod
    def getTotalDiscs(self) -> Optional[str]:
        """ get total number of discs """

    @abstractmethod
    def getTrackNumber(self) -> Optional[str]:
        """ get Track number """

    @abstractmethod
    def getTotalTracks(self) -> Optional[str]:
        """ get Total number of tracks """

    @abstractmethod
    def getComment(self) -> Optional[str]:
        """ get comment """

    @abstractmethod
    def getDate(self) -> Optional[str]:
        """ get the album release date """

    @abstractmethod
    def getCustomTag(self, key: str) -> Optional[str]:
        """ get a custom tag as Key = value """

    @abstractmethod
    def getCatalog(self) -> Optional[str]:
        """ get Catalog number """

    @abstractmethod
    def getDiscName(self) -> Optional[str]:
        """ get the name of the disc """

    @abstractmethod
    def getInformation(self) -> str:
        """ See the metadata information in Human Readable Format """

    @abstractmethod
    def save(self):
        """ Apply metadata changes """


class VorbisWrapper(IAudioManager):
    def __init__(self, mutagen_object: Union[FLAC, OggVorbis, OggOpus], extension: str):
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
        picture = PictureFLAC()
        picture.data = imageData
        picture.type = pictureType
        picture.mime = 'image/jpeg'
        picture.desc = pictureNumberToName[pictureType]
        if self.extension == '.flac':
            self.audio.add_picture(picture)
        else:
            import base64
            self.audio["metadata_block_picture"] = base64.b64encode(picture.write()).decode("ascii")

    def hasPictureOfType(self, pictureType):
        if (self.extension == '.opus' or self.extension == '.ogg') and "metadata_block_picture" in self.audio:
            return True
        elif self.extension == '.flac':
            for picture in self.audio.pictures:
                if picture.type == pictureType:
                    return True
        return False

    def deletePictureOfType(self, pictureType):
        # This will remove all pictures sadly,
        # i couldn't find any proper method to remove only one picture
        if self.extension == '.flac':
            self.audio.clear_pictures()
        elif "metadata_block_picture" in self.audio:
            self.audio.pop("metadata_block_picture")
        return True

    def setDate(self, date):
        self.audio['date'] = date

    def setCustomTag(self, key, value):
        if not isinstance(value, list):
            value = [value]
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


class CustomWAVE(WAVE):
    def add(self, frame):
        frameHashKey = frame.HashKey
        self[frameHashKey] = frame

    def getall(self, key):
        if key in self:
            return [self[key]]
        else:
            key = key + ":"
            return [v for s, v in self.items() if s.startswith(key)]


class ID3Wrapper(IAudioManager):

    def __init__(self, mutagen_object: Union[ID3, CustomWAVE], extension: str):
        self.audio = mutagen_object
        self.extension = extension.lower()

    def setTitle(self, newTitle):
        self.audio.add(TIT2(encoding=3, text=[newTitle[0]]))
        if len(newTitle) > 1:
            # Multiple titles are not supported in ID3 -> add other titles as custom tag!
            self.setCustomTag("Alternate Title", newTitle[1:])

    def setAlbum(self, newAlbum):
        self.audio.add(TALB(encoding=3, text=[newAlbum[0]]))
        if len(newAlbum) > 1:
            # Multiple Album Names are not supported in ID3 -> add other titles as custom tag!
            self.setCustomTag("Alternate Album Name", newAlbum[1:])

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
        for frame in self.audio.getall("APIC"):
            if frame.type == pictureType:
                self.audio.pop(frame.HashKey)
                return True
        return False

    def setDate(self, date):
        self.audio.add(TDRC(encoding=3, text=[date]))

    def setCustomTag(self, key, value):
        if not isinstance(value, list):
            value = [value]
        self.audio.add(TXXX(encoding=3, desc=key, text=value))

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
        ans = self.audio.get('COMM::XXX')
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
        frames = self.audio.getall("TXXX")
        for frame in frames:
            if key in frame.HashKey:
                return frame.text[0]
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


class MP4Wrapper(IAudioManager):
    def __init__(self, mutagen_object: MP4, extension: str):
        self.extension = extension.lower()
        self.audio = mutagen_object

    def setTitle(self, newTitle):
        self.audio["\xa9nam"] = newTitle

    def setAlbum(self, newAlbum):
        self.audio["\xa9alb"] = newAlbum

    def setDiscNumbers(self, discNumber, totalDiscs):
        self.audio["disk"] = [(int(discNumber), int(totalDiscs))]

    def setTrackNumbers(self, trackNumber, totalTracks):
        self.audio["trkn"] = [(int(trackNumber), int(totalTracks))]

    def setComment(self, comment):
        self.audio["\xa9cmt"] = comment

    # There is no way to set cover of a certain type here
    def setPictureOfType(self, imageData, pictureType):
        cover = MP4Cover(imageData, imageformat=MP4Cover.FORMAT_JPEG)
        self.audio["covr"] = [cover]

    def hasPictureOfType(self, pictureType):
        return "covr" in self.audio and self.audio["covr"][0].imageformat == MP4Cover.FORMAT_JPEG

    def deletePictureOfType(self, pictureType):
        if "covr" in self.audio:
            del self.audio["covr"]
            return True
        return False

    def setDate(self, date):
        self.audio["\xa9day"] = date

    def setCustomTag(self, key, value):
        newKey = f"----:com.apple.iTunes:{key}"
        if isinstance(value, list):
            value = [v.encode('utf-8') for v in value]
        else:
            value = [value.encode('utf-8')]
        self.audio[newKey] = value

    def setCatalog(self, value: str):
        self.setCustomTag('CATALOGNUMBER', value)
        self.setCustomTag('CATALOG', value)

    def setDiscName(self, value: str):
        self.setCustomTag('DISCSUBTITLE', value)

    def getTitle(self):
        return getFirstElement(self.audio.get("\xa9nam"))

    def getAlbum(self):
        return getFirstElement(self.audio.get("\xa9alb"))

    def getArtist(self):
        return getFirstElement(self.audio.get("\xa9ART"))

    def getAlbumArtist(self):
        return getFirstElement(self.audio.get("aART"))

    def getDiscNumber(self):
        disk = getFirstElement(self.audio.get("disk"))
        return str(disk[0]) if disk else None

    def getTotalDiscs(self):
        disk = getFirstElement(self.audio.get("disk"))
        return str(disk[1]) if disk else None

    def getTrackNumber(self):
        trkn = getFirstElement(self.audio.get("trkn"))
        return str(trkn[0]) if trkn else None

    def getTotalTracks(self):
        trkn = getFirstElement(self.audio.get("trkn"))
        return str(trkn[1]) if trkn else None

    def getComment(self):
        return getFirstElement(self.audio.get("\xa9cmt"))

    def getDate(self):
        return self.audio.get("\xa9day", None)

    def getCustomTag(self, key):
        newKey = f"----:com.apple.iTunes:{key}"
        value = self.audio.get(newKey, None)
        if not value:
            return None
        if isinstance(value, list):
            value = [v.decode('utf-8') for v in value]
        else:
            value = [value.decode('utf-8')]
        return getFirstElement(value)

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


audioFileHandler = {
    '.flac': [VorbisWrapper, FLAC],
    '.wav': [ID3Wrapper, CustomWAVE],
    '.mp3': [ID3Wrapper, ID3],
    '.ogg': [VorbisWrapper, OggVorbis],
    '.opus': [VorbisWrapper, OggOpus],
    '.m4a': [MP4Wrapper, MP4]
}
supportedExtensions = audioFileHandler.keys()


class AudioFactory():
    @staticmethod
    def buildAudioManager(filePath: str) -> IAudioManager:
        _, extension = os.path.splitext(filePath)
        codec = audioFileHandler[extension.lower()][0]
        handler = audioFileHandler[extension.lower()][1]
        return codec(handler(filePath), extension)


if __name__ == '__main__':
    filePath = "/run/media/arpit/DATA/Music/Visual Novels/Key Sounds Label/To Replace/[FCCM-0066] AIR SOUNDTRACK [2005.03.25]/01.wav"
    filePath = "/run/media/arpit/DATA/Downloads/test/01. Chiisana Kiseki.m4a"
    filePath = "/run/media/arpit/DATA/Downloads/test/01 - 幼くて赤い指先.flac"
    filePath = "/run/media/arpit/DATA/Downloads/test/01 - Regrets.mp3"
    audio = AudioFactory.buildAudioManager(filePath)
    audio.setCustomTag('yourssss', 'yepyep')
    audio.setTitle(['damn', 'sons'])
    audio.save()
    print(audio.getCustomTag('damnson'))
