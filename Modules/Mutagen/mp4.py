from typing import Literal

from mutagen.mp4 import MP4, MP4Cover

from Modules.Mutagen.audio_manager import IAudioManager
from Modules.Mutagen.utils import (
    cleanDate,
    convertStringToNumber,
    toList,
    getFirstElement,
    extractYearFromDate,
)


class MP4Wrapper(IAudioManager):
    def __init__(self, file_path: str, extension: Literal[".m4a"]):
        extension_handlers = {".m4a": MP4}
        self.extension = extension.lower()
        self.audio = extension_handlers[extension](file_path)

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

    # There is no way to set cover of a certain type here :( We can put multiple covers but it becomes messy without identifiers for cover type
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
        self.audio["\xa9day"] = [cleanDate(date)]
        self.audio["\xa9year"] = [extractYearFromDate(date)]

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
        return toList(self.audio.get("\xa9nam"))

    def getAlbum(self):
        return toList(self.audio.get("\xa9alb"))

    def getArtist(self):
        return toList(self.audio.get("\xa9ART"))

    def getAlbumArtist(self):
        return toList(self.audio.get("aART"))

    def getDiscNumber(self):
        disk = toList(getFirstElement(self.audio.get("disk")))
        return convertStringToNumber(disk[0]) if disk else None

    def getTotalDiscs(self):
        disk = toList(getFirstElement(self.audio.get("disk")))
        return convertStringToNumber(disk[1]) if disk else None

    def getTrackNumber(self):
        trkn = toList(getFirstElement(self.audio.get("trkn")))
        return convertStringToNumber(trkn[0]) if trkn else None

    def getTotalTracks(self):
        trkn = toList(getFirstElement(self.audio.get("trkn")))
        return convertStringToNumber(trkn[1]) if trkn else None

    def getComment(self):
        return toList(self.audio.get("\xa9cmt"))

    def getDate(self):
        date = self.audio.get("\xa9day")
        return cleanDate(date[0]) if date else None

    def getCustomTag(self, key):
        newKey = f"----:com.apple.iTunes:{key}"
        value = self.audio.get(newKey, None)
        if not value:
            return []
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

    def _searchMultiCustomTags(self, possibleFields: list[str]) -> list[str]:
        for field in possibleFields:
            ans = self.getCustomTag(field)
            if ans:
                return ans
        return []
