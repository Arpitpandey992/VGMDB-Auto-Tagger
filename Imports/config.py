from pydantic import BaseModel

# REMOVE
import os
import sys

sys.path.append(os.getcwd())
# REMOVE

from Imports.constants import LANGUAGES, TRANSLATE_LANGUAGES


class Config(BaseModel):
    # settings
    root_dir: str
    recur: bool = False
    id: str | None = None
    search: str | None = None
    yes: bool = False
    no_input: bool = False
    backup: bool = False
    backup_folder: str = "~/Music/Backups"
    no_auth: bool = False

    # Tagging:
    # Album specific flags
    tag: bool = True
    album_name: bool = True
    album_cover: bool = True
    album_cover_overwrite: bool = False
    date: bool = True
    catalog: bool = True
    barcode: bool = True
    vgmdb_link: bool = True
    organizations: bool = True
    media_format: bool = True
    # the following flags are supposed to be track specific, but in VGMDB, they are provided for entire album,
    # hence i've turned these off by default. They are turned on automatically for albums having only 1 track
    arrangers: bool = False
    composers: bool = False
    performers: bool = False
    lyricists: bool = False

    # Track specific flags
    title: bool = True
    keep_title: bool = False
    disc_numbers: bool = True
    track_numbers: bool = True

    # Rename:
    rename: bool = True
    rename_folder: bool = True
    rename_files: bool = True
    same_folder_name: bool = False
    folder_naming_template: str = "{[{date}] }{albumname}{ [{catalog}]}{ [{format}]}"

    # Extra stuff
    scans_download: bool = True
    all_lang: bool = True
    album_data_only: bool = False

    # language priority for names of various tags (title, album, composer, etc)
    language_order: list[LANGUAGES] = ["english", "translated", "romaji", "japanese", "other"]
    translate: bool = False
    translation_language: list[TRANSLATE_LANGUAGES] = ["english", "romaji"]

    def get_dynamically(self, key: str):
        """access the internal variables like a dict, will raise a KeyError if invalid key"""
        return self.__dict__[key]

    def set_dynamically(self, key: str, val):
        """set the internal variables like a dict, will raise a KeyError if invalid key"""
        self.__dict__[key] = val
