from typing_extensions import TypedDict, NotRequired, Required
from typing import Dict, Optional


class SearchAlbum(TypedDict):
    catalog: str
    category: str
    link: str
    media_format: str
    release_date: str
    titles: Dict[str, str]


class SearchAlbumData(SearchAlbum):
    title: str
    release_year: Optional[str]
    album_id: str


if __name__ == '__main__':
    test: SearchAlbumData = {
        "title": "damn",
        "album_id": "",
        "catalog": "asd",
        "category": "",
        "link": "",
        "media_format": "",
        "release_date": "",
        "release_year": "",
        "titles": {}
    }
