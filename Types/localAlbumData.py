from typing import Optional
from pydantic import BaseModel

class Track(BaseModel):
    file_path: str
    file_format: str
    title: Optional[str] = None
    album: Optional[str] = None
    date: Optional[str] = None
    catalog: Optional[str] = None
    barcode: Optional[str] = None



class Disc(BaseModel):
    tracks: list[Track]


class LocalAlbumData(BaseModel):
    """
    an object containing the data of files representing an audio album present in a file system
    """
    folder_path: str
    discs: list[Disc]
