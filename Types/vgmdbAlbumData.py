from typing import Optional
from pydantic import BaseModel


class ArrangerOrComposerOrLyricistOrPerformer(BaseModel):
    link: str
    names: dict


class Cover(BaseModel):
    full: str
    medium: str
    name: str
    thumb: str


class VgmdbTrackData(BaseModel):
    names: dict
    track_length: str


class VgmdbDiscData(BaseModel):
    disc_length: str
    name: Optional[str] = None
    tracks: list[VgmdbTrackData]  # map between track number and track data


class OrganizationOrPublisherOrDistributor(BaseModel):
    link: str
    names: dict
    role: str


class ReleasePrice(BaseModel):
    currency: str
    price: float


class VgmdbAlbumData(BaseModel):
    # data received from vgmdb.info
    link: str
    name: str
    names: dict
    discs: list[VgmdbDiscData]
    media_format: str
    notes: str
    vgmdb_link: str
    release_date: Optional[str] = None

    catalog: Optional[str] = None
    barcode: Optional[str] = None

    covers: list[Cover]
    picture_full: str
    picture_small: str
    picture_thumb: str

    arrangers: list[ArrangerOrComposerOrLyricistOrPerformer]
    composers: list[ArrangerOrComposerOrLyricistOrPerformer]
    lyricists: list[ArrangerOrComposerOrLyricistOrPerformer]
    performers: list[ArrangerOrComposerOrLyricistOrPerformer]

    classification: str
    publish_format: str
    categories: Optional[list[str]] = None
    category: Optional[str] = None
    platforms: Optional[list[str]] = None
    release_price: Optional[ReleasePrice] = None

    distributor: Optional[OrganizationOrPublisherOrDistributor] = None
    publisher: Optional[OrganizationOrPublisherOrDistributor] = None
    organizations: Optional[list[OrganizationOrPublisherOrDistributor]] = None

    # custom data
    album_id: str
