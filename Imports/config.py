import json
from typing import get_args
from pydantic import BaseModel, ValidationError, field_validator

# REMOVE
import os
import sys

sys.path.append(os.getcwd())
# REMOVE

from Imports.constants import LANGUAGES


class Config(BaseModel):
    # Settings
    BACKUPFOLDER: str = "~/Music/Backups"
    tableFormat: str = "pretty"

    # Management Flags
    backup: bool = False
    yes_to_all: bool = False
    confirm: bool = False
    RENAME_FILES: bool = True
    TAG: bool = True
    RENAME_FOLDER: bool = True
    NO_AUTH: bool = False
    NO_INPUT: bool = False
    TRANSLATE: bool = False
    IGNORE_MISMATCH: bool = False  # Dangerous, keep false

    # Metadata Flags
    # Album specific tags
    ALBUM_NAME: bool = True
    ALBUM_COVER: bool = True
    ALBUM_COVER_OVERWRITE: bool = False
    SCANS_DOWNLOAD: bool = True
    DATE: bool = True
    # YEAR: bool = True
    CATALOG: bool = True
    BARCODE: bool = True
    VGMDB_LINK: bool = True
    ORGANIZATIONS: bool = True
    # the following tags are supposed to be track specific, but in VGMDB, they are provided for entire album,
    # hence i've turned these off by default
    ARRANGERS: bool = False
    COMPOSERS: bool = False
    PERFORMERS: bool = False
    LYRICISTS: bool = False

    # Track specific tags
    TITLE: bool = True
    DISC_NUMBERS: bool = True
    TRACK_NUMBERS: bool = True
    KEEP_TITLE: bool = False
    SAME_FOLDER_NAME: bool = False
    ALL_LANG: bool = True

    # default naming templates
    folderNamingTemplate: str = "{[{date}] }{albumname}{ [{catalog}]}{ [{format}]}"
    # languages to be probed from VGMDB in the given order of priority
    language_order: list[LANGUAGES] = ["english", "romaji", "japanese", "other"]

    # misc flags
    SEE_FLAGS: bool = False

    def __init__(self, **data):
        unexpected_kwargs = set(data.keys()) - set(self.__annotations__.keys())
        if unexpected_kwargs:
            raise TypeError(f"unexpected config option{'s' if len(unexpected_kwargs) > 1 else ''}: {', '.join(unexpected_kwargs)}")
        super().__init__(**data)


flags_instance: Config | None = None


def get_config() -> Config:
    """not thread safe, just saying ;)"""

    def _init_flags() -> Config:
        """use config.json in root directory to initialize flags"""
        config_file_path = "config.json"
        with open(config_file_path, "r") as file:
            config = json.load(file)
        try:
            return Config(**config)
        except ValidationError as e:
            print(f"validation error in {config_file_path}")
            for err in e.errors():
                print(err)
            raise (e)
        except TypeError as e:
            print(f"type error in {config_file_path}")
            print(e)
            raise (e)
        except Exception as e:
            exit(0)

    global flags_instance
    if flags_instance is None:
        flags_instance = _init_flags()
    return flags_instance


if __name__ == "__main__":
    x = get_config()
    print(x.tableFormat)
    x.tableFormat = "damn_pretty"
    print(x.tableFormat)
    y = get_config()
    print(y.tableFormat)
    assert x.tableFormat == y.tableFormat
    assert x is y
