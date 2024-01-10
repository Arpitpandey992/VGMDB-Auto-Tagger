import os
import base64
from typing import Union, Optional
from abc import ABC, abstractmethod

from mutagen.mp3 import MP3
from mutagen.flac import Picture as PictureFLAC, FLAC
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.id3._frames import APIC, TALB, TDAT, TYER, TRCK, COMM, TXXX, TPOS, TIT2
from mutagen.id3 import ID3
from mutagen.mp4 import MP4, MP4Cover

from Utility.Mutagen.mutagenUtils import (
    cleanDate,
    convertStringToNumber,
    ensureOneOrNone,
    getFirstElement,
    getProperCount,
    pictureNameToNumber,
    pictureTypes,
    splitAndGetFirst,
    splitAndGetSecond,
    extractYearFromDate,
)
from Utility.generalUtils import get_default_logger


logger = get_default_logger(__name__, "info")

"""
This is a wrapper around mutagen module. 
This basically allows us to call the same functions for any extension, and hence reducing code complexity.
"""


class IAudioManager(ABC):
    """
    Interface Class for generalizing usage of Mutagen across multiple formats
    """

    @abstractmethod
    def setTitle(self, newTitle: list[str]):
        """Set the title of track"""

    @abstractmethod
    def setAlbum(self, newAlbum: list[str]):
        """Set the album name of the track"""

    @abstractmethod
    def setDiscNumbers(self, discNumber: int, totalDiscs: int):
        """
        set disc number and total number of discs
        The arguments are supposed to be a string here
        """

    @abstractmethod
    def setTrackNumbers(self, trackNumber: int, totalTracks: int):
        """
        Set Track number and total number of tracks
        The arguments are supposed to be a string here
        """

    @abstractmethod
    def setComment(self, comment: list[str]):
        """Set comment"""

    @abstractmethod
    def setPictureOfType(self, imageData: bytes, pictureType: pictureTypes):
        """Set a picture of some type (3 = front Cover)"""

    @abstractmethod
    def hasPictureOfType(self, pictureType: pictureTypes) -> bool:
        """check whether a picture of some type (3 = front Cover) is present"""

    @abstractmethod
    def deletePictureOfType(self, pictureType: pictureTypes) -> bool:
        """delete a picture of some type (3 = front Cover), returns True if picture successfully deleted"""

    @abstractmethod
    def setDate(self, date: list[str]):
        """Set the album release date"""

    @abstractmethod
    def setCustomTag(self, key: str, value: list[str]):
        """Set a custom tag as Key = value"""

    @abstractmethod
    def setCatalog(self, value: list[str]):
        """Set Catalog number"""

    @abstractmethod
    def setBarcode(self, value: list[str]):
        """Set Barcode number"""

    @abstractmethod
    def setDiscName(self, value: list[str]):
        """Set The Name of The Disc"""

    @abstractmethod
    def getTitle(self) -> Optional[list[str]]:
        """get the title of track"""

    @abstractmethod
    def getAlbum(self) -> Optional[list[str]]:
        """get the album name of the track"""

    @abstractmethod
    def getArtist(self) -> Optional[list[str]]:
        """get the artist name of the track"""

    @abstractmethod
    def getAlbumArtist(self) -> Optional[list[str]]:
        """get the album Artist name"""

    @abstractmethod
    def getDiscNumber(self) -> Optional[int]:
        """get disc number"""

    @abstractmethod
    def getTotalDiscs(self) -> Optional[int]:
        """get total number of discs"""

    @abstractmethod
    def getTrackNumber(self) -> Optional[int]:
        """get Track number"""

    @abstractmethod
    def getTotalTracks(self) -> Optional[int]:
        """get Total number of tracks"""

    @abstractmethod
    def getComment(self) -> Optional[list[str]]:
        """get comment"""

    @abstractmethod
    def getDate(self) -> Optional[list[str]]:
        """get the album release date"""

    @abstractmethod
    def getCustomTag(self, key: str) -> Optional[list[str]]:
        """get a custom tag as Key = value (which can be a string or a list of strings)"""

    @abstractmethod
    def getCatalog(self) -> Optional[list[str]]:
        """get Catalog number of the album"""

    @abstractmethod
    def getBarcode(self) -> Optional[list[str]]:
        """get Barcode of the album"""

    @abstractmethod
    def getDiscName(self) -> Optional[str]:
        """get the name of the disc"""

    @abstractmethod
    def printInfo(self) -> str:
        """See the metadata information in Human Readable Format"""

    @abstractmethod
    def getInfo(self):
        """get the info metadata object"""

    @abstractmethod
    def getExtension(self) -> int:
        """get the extension name of the file"""

    @abstractmethod
    def save(self):
        """Apply metadata changes"""

    @abstractmethod
    def clearTags(self):
        """clear all metadata tags"""


class CustomOgg(OggVorbis):
    def add_picture(self, picture: PictureFLAC):
        current_metadata_block_picture = self.get("metadata_block_picture")
        if not current_metadata_block_picture:
            current_metadata_block_picture = []
        current_metadata_block_picture.append(base64.b64encode(picture.write()).decode("ascii"))
        self.update(metadata_block_picture=current_metadata_block_picture)

    def delete_picture_of_type(self, picture_type: int):
        metadata_block_picture = self.pictures
        if metadata_block_picture:
            blocks = [b for b in metadata_block_picture if b.type != picture_type]
            self._update_metadata_picture_block(blocks)

    def clear_pictures(self):
        if "metadata_block_picture" in self:
            self.pop("metadata_block_picture")

    @property
    def pictures(self):
        metadata_block_picture = self.get("metadata_block_picture")
        if isinstance(metadata_block_picture, list):
            return [PictureFLAC(base64.b64decode(x)) for x in metadata_block_picture]
        return []

    def _update_metadata_picture_block(self, decoded_metadata_block_picture: list[PictureFLAC]):
        encoded_metadata_picture_block = [base64.b64encode(picture.write()).decode("ascii") for picture in decoded_metadata_block_picture]
        self.update(metadata_block_picture=encoded_metadata_picture_block)


class CustomOpus(OggOpus):
    def add_picture(self, picture: PictureFLAC):
        current_metadata_block_picture = self.get("metadata_block_picture")
        if not current_metadata_block_picture:
            current_metadata_block_picture = []
        current_metadata_block_picture.append(base64.b64encode(picture.write()).decode("ascii"))
        self.update(metadata_block_picture=current_metadata_block_picture)

    def delete_picture_of_type(self, picture_type: int):
        metadata_block_picture = self.pictures
        if metadata_block_picture:
            blocks = [b for b in metadata_block_picture if b.type != picture_type]
            self._update_metadata_picture_block(blocks)

    def clear_pictures(self):
        if "metadata_block_picture" in self:
            self.pop("metadata_block_picture")

    @property
    def pictures(self):
        metadata_block_picture = self.get("metadata_block_picture")
        if isinstance(metadata_block_picture, list):
            return [PictureFLAC(base64.b64decode(x)) for x in metadata_block_picture]
        return []

    def _update_metadata_picture_block(self, decoded_metadata_block_picture: list[PictureFLAC]):
        encoded_metadata_picture_block = [base64.b64encode(picture.write()).decode("ascii") for picture in decoded_metadata_block_picture]
        self.update(metadata_block_picture=encoded_metadata_picture_block)


class CustomFLAC(FLAC):
    def delete_picture_of_type(self, picture_type: int):
        blocks = [b for b in self.metadata_blocks if b.code != PictureFLAC.code or b.type != picture_type]
        self.metadata_blocks = blocks


class VorbisWrapper(IAudioManager):
    def __init__(self, mutagen_object: Union[CustomFLAC, CustomOgg, CustomOpus], extension: str):
        self.extension = extension.lower()
        self.audio = mutagen_object

    def setTitle(self, newTitle):
        self.audio["title"] = newTitle

    def setAlbum(self, newAlbum):
        self.audio["album"] = newAlbum

    def setDiscNumbers(self, discNumber, totalDiscs):
        properDiscNumber, properTotalDiscs = getProperCount(discNumber, totalDiscs)
        self.audio["discnumber"] = properDiscNumber
        self.audio["totaldiscs"] = properTotalDiscs
        self.audio["disctotal"] = properTotalDiscs

    def setTrackNumbers(self, trackNumber, totalTracks):
        properTrackNumber, properTotalTracks = getProperCount(trackNumber, totalTracks)
        self.audio["tracknumber"] = properTrackNumber
        self.audio["totaltracks"] = properTotalTracks
        self.audio["tracktotal"] = properTotalTracks

    def setComment(self, comment):
        self.audio["comment"] = comment

    def setPictureOfType(self, imageData, pictureType):
        picture = PictureFLAC()
        picture.data = imageData
        picture.type = pictureNameToNumber[pictureType]
        picture.mime = "image/jpeg"
        picture.desc = pictureType
        self.audio.add_picture(picture)

    def hasPictureOfType(self, pictureType):
        for picture in self.audio.pictures:
            if picture.type == -1 or picture.type == pictureNameToNumber[pictureType]:  # -1 for ogg/opus since they can only have one picture
                return True
        return False

    def deletePictureOfType(self, pictureType):
        if not self.hasPictureOfType(pictureType):
            return False
        self.audio.delete_picture_of_type(pictureNameToNumber[pictureType])  # Note: OGG and OPUS files can only contain one picture, so this will remove any picture stored regardless of type
        return True

    def setDate(self, date):
        self.audio["date"] = [cleanDate(current_date) for current_date in date]
        self.audio["year"] = [extractYearFromDate(current_date) for current_date in date]

    def setCustomTag(self, key, value):
        self.audio[key] = value

    def setCatalog(self, value):
        self.setCustomTag("CATALOGNUMBER", value)
        self.setCustomTag("CATALOG", value)

    def setBarcode(self, value):
        self.setCustomTag("barcode", value)

    def setDiscName(self, value):
        self.setCustomTag("DISCSUBTITLE", value)

    def getTitle(self):
        return ensureOneOrNone(self.audio.get("title"))

    def getAlbum(self):
        return ensureOneOrNone(self.audio.get("album"))

    def getArtist(self):
        return ensureOneOrNone(self.audio.get("artist"))

    def getAlbumArtist(self):
        return ensureOneOrNone(self.audio.get("albumartist"))

    def getDiscNumber(self):
        ans = getFirstElement(self.audio.get("discnumber"))
        # Usually the track number will be a simple number for Vorbis files, but sometimes it is like 01/23 which is wrong but to avoid the corner case, we are splitting it regardless
        return convertStringToNumber(splitAndGetFirst(ans))

    def getTotalDiscs(self):
        ans = self.audio.get("disctotal")
        if not ans:
            ans = self.audio.get("totaldiscs")
        if not ans:
            ans = splitAndGetSecond(getFirstElement(self.audio.get("discnumber")))
        return convertStringToNumber(getFirstElement(ans))

    def getTrackNumber(self):
        ans = getFirstElement(self.audio.get("tracknumber"))
        # Usually the track number will be a simple number for Vorbis files, but sometimes it is like 01/23 which is wrong but to avoid the corner case, we are splitting it
        return convertStringToNumber(splitAndGetFirst(ans))

    def getTotalTracks(self):
        ans = self.audio.get("tracktotal")
        if not ans:
            ans = self.audio.get("totaltracks")
        # If the answer is still None, it might be possible that the track number is instead written like 01/23 from where we can get the total tracks. However, this format of writing track number is wrong in Vorbis files.
        if not ans:
            ans = splitAndGetSecond(getFirstElement(self.audio.get("tracknumber")))
        return convertStringToNumber(getFirstElement(ans))

    def getComment(self):
        return ensureOneOrNone(self.audio.get("comment"))

    def getDate(self):
        return self._searchMultiCustomTags(["date", "ORIGINALDATE", "year", "ORIGINALYEAR"])

    def getCustomTag(self, key):
        return ensureOneOrNone(self.audio.get(key))

    def getCatalog(self):
        return self._searchMultiCustomTags(["CATALOGNUMBER", "CATALOG", "LABELNO"])

    def getBarcode(self):
        return self._searchMultiCustomTags(["barcode", "BARCODE"])

    def getDiscName(self):
        return self._searchMultiCustomTags(["DISCSUBTITLE", "DISCNAME"])

    def printInfo(self):
        return self.audio.pprint()

    def getInfo(self):
        return self.audio.info

    def getExtension(self):
        return self.extension

    def save(self):
        self.audio.save()

    def clearTags(self):
        self.audio.delete()
        self.audio.clear_pictures()

    def _searchMultiCustomTags(self, possibleFields: list[str]) -> Optional[list[str]]:
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:  # This will automatically ensure EnsureOneOrNone Condition
                return ans
        return None


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


class CustomMP3(ID3):
    def __init__(self, *args, **kwargs):
        if args:
            filePath = args[0]
            # ensuring that the file contains an ID3 tag beforehand
            audio = MP3(filePath)
            if audio.tags is None:
                audio.add_tags()
                audio.save()
            self.info = audio.info

        super().__init__(*args, **kwargs)


class ID3Wrapper(IAudioManager):
    def __init__(self, mutagen_object: Union[CustomMP3, CustomWAVE], extension: str):
        self.audio = mutagen_object
        self.extension = extension.lower()

    def setTitle(self, newTitle):
        self.audio.add(TIT2(encoding=3, text=[title for title in newTitle[:1]]))
        if len(newTitle) > 1:
            # Multiple titles are not supported in ID3 -> add other titles as custom tag!
            self.setCustomTag("Alternate Title", newTitle[1:])

    def setAlbum(self, newAlbum):
        self.audio.add(TALB(encoding=3, text=[album for album in newAlbum[:1]]))
        if len(newAlbum) > 1:
            # Multiple Album Names are not supported in ID3 -> add other titles as custom tag!
            self.setCustomTag("Alternate Album Name", newAlbum[1:])

    def setDiscNumbers(self, discNumber, totalDiscs):
        properDiscNumber, properTotalDiscs = getProperCount(discNumber, totalDiscs)
        self.audio.add(TPOS(encoding=3, text=[properDiscNumber + "/" + properTotalDiscs]))

    def setTrackNumbers(self, trackNumber, totalTracks):
        properTrackNumber, properTotalTracks = getProperCount(trackNumber, totalTracks)
        self.audio.add(TRCK(encoding=3, text=[properTrackNumber + "/" + properTotalTracks]))

    def setComment(self, comment):
        self.audio.add(COMM(encoding=3, text=comment))

    def setPictureOfType(self, imageData, pictureType):
        picture = APIC(encoding=3, mime="image/jpeg", type=pictureNameToNumber[pictureType], desc=pictureType, data=imageData)
        self.audio.add(picture)

    def hasPictureOfType(self, pictureType):
        pictures = self.audio.getall("APIC")
        if pictures:
            for picture in pictures:
                if picture.type == pictureNameToNumber[pictureType]:
                    return True
        return False

    def deletePictureOfType(self, pictureType):
        for frame in self.audio.getall("APIC"):
            if frame.type == pictureNameToNumber[pictureType]:
                self.audio.pop(frame.HashKey)
                return True
        return False

    def setDate(self, date):
        self.audio.add(TDAT(encoding=3, text=[cleanDate(current_date) for current_date in date[:1]]))
        self.audio.add(TYER(encoding=3, text=[extractYearFromDate(current_date) for current_date in date[:1]]))
        if len(date) > 1:
            # Multiple titles are not supported in ID3 -> add other titles as custom tag!
            self.setCustomTag("Alternate Date", [cleanDate(current_date) for current_date in date[1:]])

    def setCustomTag(self, key, value):
        if not value:
            self._delete_custom_tag(
                key
            )  # deleting the custom tag if exists if the provided value is an empty list. This is consistent with other predefined tags where empty list makes the tag = None
            return
        self.audio.add(TXXX(encoding=3, desc=key, text=value))

    def setCatalog(self, value):
        self.setCustomTag("CATALOGNUMBER", value)
        self.setCustomTag("CATALOG", value)

    def setBarcode(self, value):
        self.setCustomTag("barcode", value)

    def setDiscName(self, value):
        self.setCustomTag("DISCSUBTITLE", value)

    def getTitle(self):
        ans = self.audio.get("TIT2")
        if not ans or not ans.text:
            return None
        title = [x for x in ans.text]
        other_titles = self.getCustomTag("Alternate Title")
        title.extend(other_titles) if other_titles else None
        return title

    def getAlbum(self):
        ans = self.audio.get("TALB")
        if not ans or not ans.text:
            return None
        album = [x for x in ans.text]
        other_album_names = self.getCustomTag("Alternate Album Name")
        album.extend(other_album_names) if other_album_names else None
        return album

    def getArtist(self):
        ans = self.audio.get("TPE1")
        return ensureOneOrNone(ans.text) if ans else None

    def getAlbumArtist(self):
        ans = self.audio.get("TPE2")
        return ensureOneOrNone(ans.text) if ans else None

    def getDiscNumber(self):
        ans = self.audio.get("TPOS")
        return convertStringToNumber(splitAndGetFirst(getFirstElement(ans.text))) if ans else None

    def getTotalDiscs(self):
        ans = self.audio.get("TPOS")
        return convertStringToNumber(splitAndGetSecond(getFirstElement(ans.text))) if ans else None

    def getTrackNumber(self):
        ans = self.audio.get("TRCK")
        return convertStringToNumber(splitAndGetFirst(getFirstElement(ans.text))) if ans else None

    def getTotalTracks(self):
        ans = self.audio.get("TRCK")
        return convertStringToNumber(splitAndGetSecond(getFirstElement(ans.text))) if ans else None

    def getComment(self):
        ans = self.audio.get("COMM::XXX")
        return ensureOneOrNone(ans.text) if ans else None

    def getDate(self):
        ans = self.audio.get("TDAT")
        if not ans or not ans.text:
            return None
        dates = [cleanDate(str(dat)) for dat in ans.text]
        other_dates = self.getCustomTag("Alternate Date")
        dates.extend([cleanDate(str(dat)) for dat in other_dates]) if other_dates else None
        return dates

    def getCustomTag(self, key):
        frames = self.audio.getall("TXXX")
        for frame in frames:
            if key == frame.desc:
                return frame.text
        return None

    def getCatalog(self):
        return self._searchMultiCustomTags(["CATALOGNUMBER", "CATALOG", "LABELNO"])

    def getBarcode(self):
        return self._searchMultiCustomTags(["barcode", "BARCODE"])

    def getDiscName(self):
        return self._searchMultiCustomTags(["DISCSUBTITLE", "DISCNAME"])

    def printInfo(self):
        return self.audio.pprint()

    def getInfo(self):
        return self.audio.info

    def getExtension(self):
        return self.extension

    def save(self):
        self.audio.save()

    def clearTags(self):
        self.audio.delete()

    def _searchMultiCustomTags(self, possibleFields: list[str]) -> Optional[list[str]]:
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:  # This will automatically ensure EnsureOneOrNone Condition
                return ans
        return None

    def _delete_custom_tag(self, key: str):
        frames = self.audio.getall("TXXX")
        for frame in frames:
            if key == frame.desc:
                self.audio.pop(frame.HashKey)
                return


class MP4Wrapper(IAudioManager):
    def __init__(self, mutagen_object: MP4, extension: str):
        self.extension = extension.lower()
        self.audio = mutagen_object

    def setTitle(self, newTitle):
        self.audio["\xa9nam"] = newTitle

    def setAlbum(self, newAlbum):
        self.audio["\xa9alb"] = newAlbum

    def setDiscNumbers(self, discNumber, totalDiscs):
        self.audio["disk"] = [(discNumber, totalDiscs)]

    def setTrackNumbers(self, trackNumber, totalTracks):
        self.audio["trkn"] = [(trackNumber, totalTracks)]

    def setComment(self, comment):
        self.audio["\xa9cmt"] = comment

    # There is no way to set cover of a certain type here :(
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
        self.audio["\xa9day"] = [cleanDate(current_date) for current_date in date]
        self.audio["\xa9year"] = [extractYearFromDate(current_date) for current_date in date]

    def setCustomTag(self, key, value):
        newKey = f"----:com.apple.iTunes:{key}"
        value = [v.encode("utf-8") for v in value]
        self.audio[newKey] = value

    def setCatalog(self, value):
        self.setCustomTag("CATALOGNUMBER", value)
        self.setCustomTag("CATALOG", value)

    def setBarcode(self, value):
        self.setCustomTag("barcode", value)

    def setDiscName(self, value):
        self.setCustomTag("DISCSUBTITLE", value)

    def getTitle(self):
        return ensureOneOrNone(self.audio.get("\xa9nam"))

    def getAlbum(self):
        return ensureOneOrNone(self.audio.get("\xa9alb"))

    def getArtist(self):
        return ensureOneOrNone(self.audio.get("\xa9ART"))

    def getAlbumArtist(self):
        return ensureOneOrNone(self.audio.get("aART"))

    def getDiscNumber(self):
        disk = ensureOneOrNone(getFirstElement(self.audio.get("disk")))
        return disk[0] if disk else None

    def getTotalDiscs(self):
        disk = ensureOneOrNone(getFirstElement(self.audio.get("disk")))
        return disk[1] if disk else None

    def getTrackNumber(self):
        trkn = ensureOneOrNone(getFirstElement(self.audio.get("trkn")))
        return trkn[0] if trkn else None

    def getTotalTracks(self):
        trkn = ensureOneOrNone(getFirstElement(self.audio.get("trkn")))
        return trkn[1] if trkn else None

    def getComment(self):
        return ensureOneOrNone(self.audio.get("\xa9cmt"))

    def getDate(self):
        return ensureOneOrNone(self.audio.get("\xa9day", None))

    def getCustomTag(self, key):
        newKey = f"----:com.apple.iTunes:{key}"
        value = self.audio.get(newKey, None)
        if not value:
            return None
        value = [v.decode("utf-8") for v in value]
        return value

    def getCatalog(self):
        return self._searchMultiCustomTags(["CATALOGNUMBER", "CATALOG", "LABELNO"])

    def getBarcode(self):
        return self._searchMultiCustomTags(["barcode", "BARCODE"])

    def getDiscName(self):
        return self._searchMultiCustomTags(["DISCSUBTITLE", "DISCNAME"])

    def printInfo(self):
        return self.audio.pprint()

    def getInfo(self):
        return self.audio.info

    def getExtension(self):
        return self.extension

    def save(self):
        self.audio.save()

    def clearTags(self):
        self.audio.delete()

    def _searchMultiCustomTags(self, possibleFields: list[str]) -> Optional[list[str]]:
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:  # This will automatically ensure EnsureOneOrNone Condition
                return ans
        return None


audioFileHandler = {
    ".flac": [VorbisWrapper, CustomFLAC],
    ".wav": [ID3Wrapper, CustomWAVE],
    ".mp3": [ID3Wrapper, CustomMP3],
    ".ogg": [VorbisWrapper, CustomOgg],
    ".opus": [VorbisWrapper, CustomOpus],
    ".m4a": [MP4Wrapper, MP4],
}
supportedExtensions = audioFileHandler.keys()


class AudioFactory:
    @staticmethod
    def buildAudioManager(filePath: str) -> IAudioManager:
        _, extension = os.path.splitext(filePath)
        codec = audioFileHandler[extension.lower()][0]
        handler = audioFileHandler[extension.lower()][1]
        return codec(handler(filePath), extension)


if __name__ == "__main__":
    filePath = "/Users/arpit/Library/Custom/Downloads/example.mp3"
    audio = AudioFactory.buildAudioManager(filePath)
    print(type(audio))
    print(isinstance(audio, IAudioManager))
    audio.setCustomTag("yourssss", ["yepyep", "ei", "213dasfdad"])
    audio.setTitle(["damn", "sons", "huh"])
    audio.setComment(["This is a comment", "This as well", "maybe this one too ;)"])
    audio.save()
    print(audio.printInfo())
