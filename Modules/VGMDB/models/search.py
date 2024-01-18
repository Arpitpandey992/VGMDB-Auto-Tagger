from pydantic import BaseModel

from Imports.constants import LANGUAGES
from Modules.Mutagen.utils import extractYearFromDate
from Modules.VGMDB.models.vgmdb_album_data import Names


class SearchAlbum(BaseModel):
    catalog: str
    category: str
    link: str
    media_format: str
    release_date: str
    titles: Names

    @property
    def album_id(self) -> str:
        return self.link.split("/")[-1]

    @property
    def release_year(self) -> str | None:
        return extractYearFromDate(self.release_date)

    @property
    def album_link(self) -> str:
        return f"https://vgmdb.net/{self.link}"

    def get_album_name(self, language_order: list[LANGUAGES]) -> str:
        name = self.titles.get_highest_priority_name(language_order)
        return name if name else ""
