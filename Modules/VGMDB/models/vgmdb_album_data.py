import os
from typing import get_args
from pydantic import BaseModel

from Imports.constants import languages
from Modules.Print.utils import LINE_SEPARATOR, SUB_LINE_SEPARATOR
from Modules.Utils.image_utils import compress_image_limit_max_width
from Modules.Utils.network_utils import downloadFile, getRawDataFromUrl
from Modules.VGMDB.vgmdbrip.vgmdbrip import downloadScans

language_aliases: dict[languages, list[str]] = {
    "romaji": ["ja-latn", "Romaji", "Romaji Translated"],
    "english": ["en", "English", "English (Apple Music)", "English/German", "English localized", "English (alternate)", "English Translated", "English [Translation]"],
    "japanese": ["ja", "Japanese"],
}


class Names(BaseModel):
    english: list[str] = []
    japanese: list[str] = []
    romaji: list[str] = []
    others: list[str] = []

    def __init__(self, **language_dict):
        super().__init__()
        language_map: dict[languages, list[str]] = {"english": self.english, "japanese": self.japanese, "romaji": self.romaji, "other": self.others}
        for language_key, value in language_dict.items():
            identified_language = self._identify_language(language_key)
            language_map[identified_language].append(value)

    def _identify_language(self, s: str) -> languages:
        lang = s.lower().strip()
        for language_key in get_args(languages):
            if language_key in lang:
                return language_key
            for language_alias in language_aliases[language_key]:
                if language_alias.lower() == lang:
                    return language_key
        return "other"


class Cover(BaseModel):
    full: str
    medium: str
    name: str
    thumb: str


class VgmdbTrackData(BaseModel):
    names: Names
    track_length: str


class VgmdbDiscData(BaseModel):
    disc_length: str
    name: str | None = None
    tracks: dict[int, VgmdbTrackData]  # map between track number and track data


class ArrangerOrComposerOrLyricistOrPerformer(BaseModel):
    names: Names
    link: str | None = None


class OrganizationOrPublisherOrDistributor(BaseModel):
    names: Names
    link: str | None = None
    role: str


class ReleasePrice(BaseModel):
    currency: str
    price: float


class VgmdbAlbumData(BaseModel):
    # data received from vgmdb.info
    link: str
    name: str
    names: Names
    discs: dict[int, VgmdbDiscData]  # changed from list to dict for ease of use
    media_format: str
    notes: str
    vgmdb_link: str
    release_date: str | None = None

    catalog: str | None = None
    barcode: str | None = None

    covers: list[Cover]
    picture_full: str | None
    picture_small: str | None
    picture_thumb: str | None

    arrangers: list[ArrangerOrComposerOrLyricistOrPerformer]
    composers: list[ArrangerOrComposerOrLyricistOrPerformer]
    lyricists: list[ArrangerOrComposerOrLyricistOrPerformer]
    performers: list[ArrangerOrComposerOrLyricistOrPerformer]

    classification: str
    publish_format: str
    categories: list[str] | None = None
    category: str | None = None
    platforms: list[str] | None = None
    release_price: ReleasePrice | None = None

    distributor: OrganizationOrPublisherOrDistributor | None = None
    publisher: OrganizationOrPublisherOrDistributor | None = None
    organizations: list[OrganizationOrPublisherOrDistributor] | None = None

    # custom data
    album_id: str
    album_cover_cache: bytes | None = None

    # helper functions
    def get_album_cover_data(self) -> bytes | None:
        if not self.picture_full:
            return None
        if self.album_cover_cache:
            return self.album_cover_cache
        self.album_cover_cache = getRawDataFromUrl(self.picture_full)
        return compress_image_limit_max_width(self.album_cover_cache)

    def download_scans(self, output_dir: str, no_auth: bool = False):
        if no_auth:
            self._downloadScansNoAuth(output_dir)
        else:
            downloadScans(output_dir, self.album_id)

    def pprint(self) -> str:
        """pretty printing only the useful information"""
        details = f"{LINE_SEPARATOR}\nalbum name: {self.name}\n{LINE_SEPARATOR}\n"
        for disc_number, disc in sorted(self.discs.items()):
            details += f"Disc {disc_number}:{f' {disc.name}' if disc.name else ''}\n{SUB_LINE_SEPARATOR}\n"
            for track_number, track in sorted(disc.tracks.items()):
                details += f"Track {track_number}: {track.names}\n"
            details += f"{SUB_LINE_SEPARATOR}\n"
        details += f"{LINE_SEPARATOR}\n"
        return details

    def does_track_exist(self, disc_number: int, track_number: int) -> bool:
        if disc_number not in self.discs or track_number not in self.discs[disc_number].tracks:
            return False
        return True

    def get_track(self, disc_number: int, track_number: int) -> VgmdbTrackData:
        """Raises KeyError if track does not exist, use this function in conjunction with does_track_exist"""
        try:
            return self.discs[disc_number].tracks[track_number]
        except KeyError:
            raise KeyError(f"no track exists having disc number: {disc_number} and track number: {track_number}")

    # private functions
    def _downloadScansNoAuth(self, output_dir: str):
        frontPictureExists = False
        coverPath = os.path.join(output_dir, "Scans")
        if not os.path.exists(coverPath):
            os.makedirs(coverPath)
        for cover in self.covers:
            downloadFile(url=cover.full, output_dir=coverPath, name=cover.name)
            if cover.name.lower() == "front" or cover.name.lower == "cover":
                frontPictureExists = True
        if not frontPictureExists and self.picture_full:
            downloadFile(url=self.picture_full, output_dir=coverPath, name="Front")
