from tap import Tap
from Imports.config import Config

from Utility.template import TemplateResolver


class CLIArgs(Tap):
    root_dir: str  # Album root directory (Required Argument)
    recur: bool = False  # recursively check the directory for albums
    id: str | None = None  # Provide Album ID to avoid searching for the album
    search: str | None = None  # Provide Custom Search Term
    yes: bool = False  # Skip Yes prompt, and when only 1 album comes up in search results
    no_input: bool = False  # Go full auto mode, and only tag those albums where no user input is required!
    backup: bool = False  # Backup the albums before modifying
    backup_folder: str = "~/Music/Backups"  # folder to backup the albums to before modification
    no_auth: bool = False  # Do not authenticate for downloading Scans

    no_tag: bool = False  # Do not tag the files
    no_rename: bool = False  # Do not rename or move anything
    no_modify: bool = False  # Do not tag or rename, for searching and testing

    no_rename_folder: bool = False  # Do not Rename the containing folder?
    no_rename_files: bool = False  # Do not rename the files
    same_folder_name: bool = False  # While renaming the folder, use the current folder name instead of getting it from album name
    folder_naming_template: str | None = None  # Give a folder naming template like "{[{catalog}] }{albumname}{ [{date}]}"
    ksl: bool = False  # for KSL folder, (custom setting), keep catalog first in naming

    no_title: bool = False  # Do not touch track titles
    keep_title: bool = False  # Keep the current title and add other available titles
    no_scans: bool = False  # Do not download Scans
    no_cover: bool = False  # Do not embed album cover into files
    cover_overwrite: bool = False  # Overwrite album cover within files

    one_lang: bool = False  # For tags with multiple values, only keep the highest priority one
    translate: bool = False  # Translate all text to english
    album_data_only: bool = False  # Only tag album specific details to ALL files in the folder, this option will tag those files as well which are not matching with any track in albumData received from VGMDB. Thus, this is a dangerous option, be careful

    performers: bool = False  # tag performers in the files
    arrangers: bool = False  # tag arrangers in the files
    composers: bool = False  # tag composers in the files
    lyricists: bool = False  # tag lyricists in the files

    english: bool = False  # Give Priority to English
    romaji: bool = False  # Give Priority to Romaji
    japanese: bool = False  # Give Priority to Japanese

    def configure(self):
        self.add_argument("root_dir")
        self.add_argument("-r", "--recur")
        self.add_argument("-y", "--yes")

    def process_args(self):
        if self.folder_naming_template:
            TemplateResolver.validateTemplate(self.folder_naming_template)  # will raise exception if not valid

    def get_config(self) -> Config:
        config = Config(**{k: v for k, v in self.as_dict().items() if v})  # Removing None values first

        if self.no_modify:
            config.tag = False
            config.rename = False
        if self.no_tag:
            config.tag = False
        if self.no_rename:
            config.rename = False

        if self.no_rename_folder:
            config.rename_folder = False
        if self.no_rename_files:
            config.rename_files = False
        if self.ksl:
            config.folder_naming_template = "{[{catalog}] }{albumname}{ [{date}]}{ [{format}]}"

        if self.no_title:
            config.title = False
        if self.no_scans:
            config.scans_download = False
        if self.no_cover:
            config.album_cover = False
        if self.cover_overwrite:
            config.album_cover_overwrite = True

        if self.one_lang:
            config.all_lang = False
        if self.album_data_only:
            config.rename_files = False

        if self.performers:
            config.performers = True
        if self.arrangers:
            config.arrangers = True
        if self.lyricists:
            config.lyricists = True
        if self.composers:
            config.composers = True

        elif self.english:
            config.language_order = ["english", "translated", "romaji", "japanese", "other"]
        elif self.romaji:
            config.language_order = ["romaji", "english", "translated", "japanese", "other"]
        if self.japanese:
            config.language_order = ["japanese", "romaji", "translated", "english", "other"]

        return config
