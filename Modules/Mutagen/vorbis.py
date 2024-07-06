import base64
from typing import Literal

from mutagen.flac import Picture as PictureFLAC, FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus

from Modules.Mutagen.audio_manager import IAudioManager
from Modules.Mutagen.utils import (
    pictureNameToNumber,
    cleanDate,
    convertStringToNumber,
    toList,
    getFirstElement,
    getProperCount,
    splitAndGetFirst,
    splitAndGetSecond,
    extractYearFromDate,
)


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
    def __init__(self, file_path: str, extension: Literal[".flac", ".ogg", ".opus"]):
        extension_handlers = {".flac": CustomFLAC, ".ogg": CustomOgg, ".opus": CustomOpus}
        self.extension = extension.lower()
        self.audio = extension_handlers[extension](file_path)

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
        self.audio.delete_picture_of_type(pictureNameToNumber[pictureType])
        return True

    def setDate(self, date):
        self.audio["date"] = [cleanDate(date)]
        self.audio["year"] = [extractYearFromDate(date)]

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
        return toList(self.audio.get("title"))

    def getAlbum(self):
        return toList(self.audio.get("album"))

    def getArtist(self):
        return toList(self.audio.get("artist"))

    def getAlbumArtist(self):
        return toList(self.audio.get("albumartist"))

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
        return toList(self.audio.get("comment"))

    def getCustomTag(self, key):
        return toList(self.audio.get(key))

    def getDate(self):
        date = self._searchMultiCustomTags(["date", "ORIGINALDATE", "year", "ORIGINALYEAR"])
        return cleanDate(date[0]) if date else None

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
        self.audio.clear_pictures()
        self.audio.delete()

    def _searchMultiCustomTags(self, possibleFields: list[str]) -> list[str]:
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:
                return ans
        return []
