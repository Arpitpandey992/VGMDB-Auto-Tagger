from typing_extensions import TypedDict, NotRequired


class ArrangerOrComposerOrLyricistOrPerformer(TypedDict):
    link: str
    names: dict[str, str]


class Cover(TypedDict):
    full: str
    medium: str
    name: str
    thumb: str


class Track(TypedDict):
    names: dict[str, str]
    track_length: str


class Disc(TypedDict):
    disc_length: str
    name: NotRequired[str]
    tracks: list[Track]


class OrganizationOrPublisherOrDistributor(TypedDict):
    link: str
    names: dict[str, str]
    role: str


class ReleasePrice(TypedDict):
    currency: str
    price: float


class AlbumData(TypedDict):
    # data received from vgmdb.info
    name: str
    names: dict[str, str]
    release_date: str
    discs: list[Disc]
    media_format: str
    link: str
    vgmdb_link: str
    notes: str

    catalog: NotRequired[str]
    barcode: NotRequired[str]

    covers: NotRequired[list[Cover]]
    picture_full: NotRequired[str]
    picture_small: NotRequired[str]
    picture_thumb: NotRequired[str]

    arrangers: NotRequired[list[ArrangerOrComposerOrLyricistOrPerformer]]
    composers: NotRequired[list[ArrangerOrComposerOrLyricistOrPerformer]]
    lyricists: NotRequired[list[ArrangerOrComposerOrLyricistOrPerformer]]
    performers: NotRequired[list[ArrangerOrComposerOrLyricistOrPerformer]]

    categories: NotRequired[list[str]]
    category: NotRequired[str]
    classification: NotRequired[str]
    platforms: NotRequired[list[str]]
    publish_format: NotRequired[str]
    release_price: NotRequired[ReleasePrice]

    distributor: NotRequired[OrganizationOrPublisherOrDistributor]
    publisher: NotRequired[OrganizationOrPublisherOrDistributor]
    organizations: NotRequired[list[OrganizationOrPublisherOrDistributor]]

    # custom data
    album_id: NotRequired[str]


class TrackData(AlbumData):
    file_path: str

    track_number: int
    total_tracks: int
    disc_number: int
    total_discs: int

    track_titles: dict[str, str]
    album_link: str
    album_names: dict[str, str]
    album_name: str

    picture_cache: NotRequired[bytes]
