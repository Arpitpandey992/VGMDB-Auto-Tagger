from typing import Union, List, Optional
from typing_extensions import TypedDict, NotRequired, Required

class NamesAbbreviated(TypedDict):
    en: NotRequired[str]
    ja: NotRequired[str]
    ja_latn: NotRequired[str]


class ArrangerOrComposerOrLyricistOrPerformer(TypedDict):
    link: str
    names: NamesAbbreviated


class Cover(TypedDict):
    full: NotRequired[str]
    medium: NotRequired[str]
    name: NotRequired[str]
    thumb: NotRequired[str]


class NamesFull(TypedDict):
    English: NotRequired[str]
    Japanese: NotRequired[str]
    Romaji: NotRequired[str]


class Track(TypedDict):
    names: NamesFull
    track_length: str


class Disc(TypedDict):
    disc_length: str
    name: NotRequired[str]
    tracks: List[Track]


class OrganizationOrPublisherOrDistributor(TypedDict):
    link: str
    names: NamesAbbreviated
    role: str


class ReleasePrice(TypedDict):
    currency: str
    price: float


class AlbumData(TypedDict):
    arrangers: List[ArrangerOrComposerOrLyricistOrPerformer]
    barcode: NotRequired[str]
    catalog: NotRequired[str]
    categories: List[str]
    category: str
    classification: str
    composers: List[ArrangerOrComposerOrLyricistOrPerformer]
    covers: List[Cover]
    discs: List[Disc]
    distributor: OrganizationOrPublisherOrDistributor
    link: str
    lyricists: List[ArrangerOrComposerOrLyricistOrPerformer]
    media_format: str
    name: str
    names: NamesAbbreviated
    notes: str
    organizations: List[OrganizationOrPublisherOrDistributor]
    performers: List[ArrangerOrComposerOrLyricistOrPerformer]
    picture_full: str
    picture_small: str
    picture_thumb: str
    platforms: List[str]
    publish_format: str
    publisher: OrganizationOrPublisherOrDistributor
    release_date: str
    release_price: ReleasePrice
    vgmdb_link: str


data:AlbumData = {
    "arrangers":[],
}