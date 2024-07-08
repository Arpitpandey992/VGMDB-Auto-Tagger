from typing import Any, Optional
from abc import ABC, abstractmethod

from Modules.Mutagen.utils import pictureTypes
from Modules.Utils.general_utils import get_default_logger


logger = get_default_logger(__name__, "info")

"""
This is a wrapper around mutagen module. 
It allows us to call the same functions for any supported extension, and hence reducing code complexity.
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
        """

    @abstractmethod
    def setTrackNumbers(self, trackNumber: int, totalTracks: int):
        """
        Set Track number and total number of tracks
        """

    @abstractmethod
    def setComment(self, comment: list[str]) -> None:
        """Set comment"""

    @abstractmethod
    def setPictureOfType(self, imageData: bytes, pictureType: pictureTypes) -> None:
        """Set a picture of some type"""

    @abstractmethod
    def hasPictureOfType(self, pictureType: pictureTypes) -> bool:
        """check whether a picture of some type (3 = front Cover) is present"""

    @abstractmethod
    def deletePictureOfType(self, pictureType: pictureTypes) -> bool:
        """delete a picture of some type (3 = front Cover), returns True if picture successfully deleted"""

    @abstractmethod
    def setDate(self, date: str) -> None:
        """Set the album release date"""

    @abstractmethod
    def setCustomTag(self, key: str, value: list[str]) -> None:
        """Set a custom tag as Key = value"""

    @abstractmethod
    def setCatalog(self, value: list[str]) -> None:
        """Set Catalog number"""

    @abstractmethod
    def setBarcode(self, value: list[str]) -> None:
        """Set Barcode number"""

    @abstractmethod
    def setDiscName(self, value: list[str]) -> None:
        """Set The Name of The Disc"""

    @abstractmethod
    def getTitle(self) -> list[str]:
        """get the title of track"""

    @abstractmethod
    def getAlbum(self) -> list[str]:
        """get the album name of the track"""

    @abstractmethod
    def getArtist(self) -> list[str]:
        """get the artist name of the track"""

    @abstractmethod
    def getAlbumArtist(self) -> list[str]:
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
    def getComment(self) -> list[str]:
        """get comment"""

    @abstractmethod
    def getDate(self) -> Optional[str]:
        """get the album release date"""

    @abstractmethod
    def getCustomTag(self, key: str) -> list[str]:
        """get a custom tag as Key = value (which can be a string or a list of strings)"""

    @abstractmethod
    def getCatalog(self) -> list[str]:
        """get Catalog number of the album"""

    @abstractmethod
    def getBarcode(self) -> list[str]:
        """get Barcode of the album"""

    @abstractmethod
    def getDiscName(self) -> list[str]:
        """get the name of the disc"""

    @abstractmethod
    def printInfo(self) -> str:
        """See the metadata information in Human Readable Format"""

    @abstractmethod
    def getInfo(self) -> Any:
        """get the info metadata object"""

    @abstractmethod
    def getExtension(self) -> str:
        """get the extension name of the file"""

    @abstractmethod
    def save(self) -> None:
        """Apply metadata changes"""

    @abstractmethod
    def clearTags(self) -> None:
        """clear all metadata tags"""
