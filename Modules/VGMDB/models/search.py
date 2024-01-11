from typing_extensions import TypedDict
from typing import Optional

from pydantic import BaseModel


class SearchAlbum(BaseModel):
    catalog: str
    category: str
    link: str
    media_format: str
    release_date: str
    titles: dict[str, str]


class SearchAlbumData(SearchAlbum):
    album_id: str
    release_year: Optional[str] = None
    title: str


if __name__ == '__main__':
    test = SearchAlbumData(**{
        "title": "damn",
        "album_id": "damn_son",
        "catalog": "what_the_hell_son?",
        "category": "where_did_you_find_this?",
        "link": "",
        "media_format": "",
        "release_date": "",
        "release_year": "",
        "titles": {}
    })
    print(test)
