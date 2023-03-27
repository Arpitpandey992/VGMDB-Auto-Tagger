from typing import List, Dict, Optional
from typing_extensions import TypedDict, NotRequired


class ArrangerOrComposerOrLyricistOrPerformer(TypedDict):
    link: str
    names: Dict[str, str]


class Cover(TypedDict):
    full: str
    medium: str
    name: str
    thumb: str


class Track(TypedDict):
    names: Dict[str, str]
    track_length: str


class Disc(TypedDict):
    disc_length: str
    name: NotRequired[str]
    tracks: List[Track]


class OrganizationOrPublisherOrDistributor(TypedDict):
    link: str
    names: Dict[str, str]
    role: str


class ReleasePrice(TypedDict):
    currency: str
    price: float


class AlbumData(TypedDict):
    # data received from vgmdb.info
    name: str
    names: Dict[str, str]
    release_date: str
    discs: List[Disc]
    media_format: str
    link: str
    vgmdb_link: str
    notes: str

    catalog: NotRequired[str]
    barcode: NotRequired[str]

    covers: NotRequired[List[Cover]]
    picture_full: NotRequired[str]
    picture_small: NotRequired[str]
    picture_thumb: NotRequired[str]

    arrangers: NotRequired[List[ArrangerOrComposerOrLyricistOrPerformer]]
    composers: NotRequired[List[ArrangerOrComposerOrLyricistOrPerformer]]
    lyricists: NotRequired[List[ArrangerOrComposerOrLyricistOrPerformer]]
    performers: NotRequired[List[ArrangerOrComposerOrLyricistOrPerformer]]

    categories: NotRequired[List[str]]
    category: NotRequired[str]
    classification: NotRequired[str]
    platforms: NotRequired[List[str]]
    publish_format: NotRequired[str]
    release_price: NotRequired[ReleasePrice]

    distributor: NotRequired[OrganizationOrPublisherOrDistributor]
    publisher: NotRequired[OrganizationOrPublisherOrDistributor]
    organizations: NotRequired[List[OrganizationOrPublisherOrDistributor]]

    # custom data
    album_id: NotRequired[str]


class TrackData(AlbumData):
    file_path: str

    track_number: int
    total_tracks: int
    disc_number: int
    total_discs: int

    track_titles: Dict[str, str]
    album_link: str
    album_names: Dict[str, str]
    album_name: str

    picture_cache: NotRequired[bytes]
