from typing import Any
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

    # Organization:
    organize: bool = True
    confirm_organize: bool = True
    rename_folder: bool = True
    rename_files: bool = True
    same_folder_name: bool = False
    folder_naming_template: str = "{[{date|year}] }{albumname|foldername}{ [{catalog}]}{ [{format}]}"
    file_naming_template_single: str = "{tracktitle|filename}{extension}"
    file_naming_template_multiple: str = "{{{tracknumber|sortnumber}. {tracktitle}}|filename}{extension}"
    disc_folder_naming_template_single: str = ""
    disc_folder_naming_template_multiple: str = "{Disc {discnumber}. {discname}}|discfoldername"

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

    def set_dynamically(self, key: str, val: Any):
        """set the internal variables like a dict, will raise a KeyError if invalid key"""
        self.__dict__[key] = val


config_cache: dict[str, Any] = {}


def get_config(root_dir: str, **kwargs: Any):
    global config_cache
    if root_dir in config_cache:
        return config_cache[root_dir]
    config_cache[root_dir] = Config(root_dir=root_dir, **kwargs)
    return config_cache[root_dir]


if __name__ == "__main__":
    obj1 = get_config(root_dir="damn")
    obj2 = get_config(root_dir="son")
    obj3 = get_config(root_dir="damn")
    print(obj1 is obj2)
    print(obj1 is obj3)
