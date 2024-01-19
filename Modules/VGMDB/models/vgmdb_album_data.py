import os
from typing import get_args
from pydantic import BaseModel, field_validator

from Imports.constants import LANGUAGES
from Modules.Print.utils import LINE_SEPARATOR, SUB_LINE_SEPARATOR
from Modules.Scan.models.local_album_data import LocalAlbumData, LocalTrackData
from Modules.Utils.image_utils import compress_image_limit_max_width
from Modules.Utils.network_utils import downloadFile, getRawDataFromUrl
from Modules.VGMDB.vgmdbrip.vgmdbrip import downloadScans

language_aliases: dict[LANGUAGES, list[str]] = {
    "english": ["en", "English", "English (Apple Music)", "English/German", "English (alternate)", "English localized", "English Translated", "English [Translation]"],  # these translations are official
    "translated": [],
    "romaji": ["ja-latn", "Romaji"],
    "japanese": ["ja", "Japanese"],
}


class Names(BaseModel):
    english: list[str] = []
    translated: list[str] = []
    japanese: list[str] = []
    romaji: list[str] = []
    others: list[str] = []

    language_map: dict[LANGUAGES, list[str]] = {}

    def __init__(self, **language_dict):
        # for identifying whether the incoming data is from a pre existing Names object:
        if "language_map" in language_dict:
            super().__init__(**language_dict)
            return
        super().__init__()
        self.language_map = {"english": self.english, "translated": self.translated, "japanese": self.japanese, "romaji": self.romaji, "other": self.others}
        for language_key, value in language_dict.items():
            identified_language = self._identify_language(language_key)
            self.language_map[identified_language].append(value)

    def add_name(self, name: str, language: LANGUAGES):
        self.language_map[language].append(name)

    def clear_names(self, language: LANGUAGES):
        self.language_map[language].clear()

    def get_reordered_names(self, order: list[LANGUAGES]) -> list[str]:
        """get all names reordered according to the given order"""
        return [name for lang in order for name in self.language_map[lang]]

    def get_highest_priority_name(self, priority: list[LANGUAGES] = ["english", "translated", "romaji", "japanese", "other"]) -> str | None:
        """get the name with highest priority"""
        reordered_names = self.get_reordered_names(priority)
        return reordered_names[0] if reordered_names else None

    def _identify_language(self, s: str) -> LANGUAGES:
        lang = s.lower().strip()
        for language_key in get_args(LANGUAGES):
            if language_key in lang:
                return language_key
            for language_alias in language_aliases[language_key]:
                if language_alias.lower() == lang:
                    return language_key
        return "other"


class Cover(BaseModel):
    full: str
    name: str
    medium: str | None = None
    thumb: str | None = None


class VgmdbTrackData(BaseModel):
    names: Names
    track_length: str | None = None
    local_track: LocalTrackData | None = None  # custom data to be used during tagging


class VgmdbDiscData(BaseModel):
    tracks: dict[int, VgmdbTrackData]  # map between track number and track data
    disc_length: str | None = None
    name: str | None = None

    @property
    def total_tracks(self) -> int:
        return len(self.tracks)


class ArrangerOrComposerOrLyricistOrPerformer(BaseModel):
    names: Names
    link: str | None = None


class OrganizationOrPublisherOrDistributor(BaseModel):
    names: Names
    role: str
    link: str | None = None


class ReleasePrice(BaseModel):
    currency: str | None = None
    price: float | None = None


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

    covers: list[Cover] = []
    picture_full: str | None
    picture_small: str | None
    picture_thumb: str | None

    arrangers: list[ArrangerOrComposerOrLyricistOrPerformer]
    composers: list[ArrangerOrComposerOrLyricistOrPerformer]
    lyricists: list[ArrangerOrComposerOrLyricistOrPerformer]
    performers: list[ArrangerOrComposerOrLyricistOrPerformer]

    classification: str | None = None
    publish_format: str | None = None
    categories: list[str] | None = None
    category: str | None = None
    platforms: list[str] | None = None
    release_price: ReleasePrice | None = None

    distributor: OrganizationOrPublisherOrDistributor | None = None
    publisher: OrganizationOrPublisherOrDistributor | None = None
    organizations: list[OrganizationOrPublisherOrDistributor] | None = None

    # custom data
    album_id: str
    unmatched_local_tracks: list[LocalTrackData] = []
    album_cover_cache: bytes | None = None

    @property
    def total_discs(self):
        return len(self.discs)

    @property
    def total_tracks_in_album(self):
        return sum(len(disc.tracks) for disc in self.discs.values())

    @field_validator("catalog", mode="before")
    @classmethod
    def fix_catalog(cls, catalog: str) -> str | None:
        return catalog if catalog != "N/A" else None

    @field_validator("discs", mode="before")
    @classmethod
    def convert_discs_from_list_to_dict(cls, discs: list | dict[int, VgmdbDiscData]) -> dict[int, VgmdbDiscData]:
        if isinstance(discs, dict) and all(isinstance(disc, VgmdbDiscData) for disc in discs.values()):
            # if we initializing this object with the proper value it is expecting
            return discs
        if isinstance(discs, list):
            # Converting disc data from list to dict which is much faster to retrieve from
            new_discs: dict[int, VgmdbDiscData] = {}
            disc_number = 1
            for disc in discs:
                new_tracks: dict[int, VgmdbTrackData] = {}
                track_number = 1
                for track in disc["tracks"]:
                    new_tracks[track_number] = VgmdbTrackData.model_validate(track)
                    track_number += 1
                new_discs[disc_number] = VgmdbDiscData(tracks=new_tracks)
                disc_number += 1
            return new_discs

        raise TypeError(f"invalid initialization of discs: {discs}")

    # helper functions
    def link_local_album_data(self, local_album_data: LocalAlbumData):
        """function for linking local files with vgmdb tracks"""
        # filling unmatched local tracks
        temp_unmatched_local_tracks_set = set()
        temp_unmatched_local_tracks_set.update(local_album_data.get_all_tracks())
        # Firstly, using a simple algorithm to link files according to matching disc number and track number
        for disc_number, disc in self.discs.items():
            for track_number, track in disc.tracks.items():
                local_track = local_album_data.get_track(disc_number, track_number)
                if local_track:
                    track.local_track = local_track
                    temp_unmatched_local_tracks_set.discard(local_track)
        # add more matching algorithms...
        self.unmatched_local_tracks = list(temp_unmatched_local_tracks_set)  # update the unmatched list

    def get_album_cover_data(self) -> bytes | None:
        if not self.picture_full:
            return None
        if self.album_cover_cache:
            return self.album_cover_cache
        self.album_cover_cache = compress_image_limit_max_width(getRawDataFromUrl(self.picture_full))
        return self.album_cover_cache

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

    def get_track(self, disc_number: int, track_number: int) -> VgmdbTrackData | None:
        return self.discs[disc_number].tracks[track_number] if self._does_track_exist(disc_number, track_number) else None

    # private functions
    def _does_track_exist(self, disc_number: int, track_number: int) -> bool:
        if disc_number not in self.discs or track_number not in self.discs[disc_number].tracks:
            return False
        return True

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


def test():
    from Modules.VGMDB.api.client import get_album_details

    data = get_album_details("123")
    print(data.pprint())
    new_data = VgmdbAlbumData(**data.model_dump())


if __name__ == "__main__":
    test()
