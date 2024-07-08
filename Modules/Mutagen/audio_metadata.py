from pydantic import BaseModel

"""
Audio metadata information, unfinished currently
to be used by metadata server
"""


class AudioMetadata(BaseModel):
    title: list[str]
    album: list[str]
    artist: list[str]
    album_artist: list[str]

    disc_number: int | None
    total_discs: int | None
    track_number: int | None
    total_tracks: int | None

    comment: list[str]
    date: str | None
    year: str | None
    catalog: list[str]
    barcode: list[str]
    disc_name: list[str]
    custom_tags: dict[str, list[str]]
