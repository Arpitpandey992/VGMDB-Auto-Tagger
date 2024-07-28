import json
import os
from tap import Tap
from typing import Any
from rich import get_console

from Imports.config import Config, get_config
from Modules.Organize.template import TemplateResolver, TemplateValidationException


class CLIArgs(Tap):
    """Automatically Tag Local Albums using Album Data from VGMDB.net!"""

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

    no_rename_folder: bool = False  # Do not Rename the containing folder
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
    translate: bool = False  # Translate all text to English and Romaji
    album_data_only: bool = False  # Only tag album specific details to ALL files in the folder, this option will tag those files as well which are not matching with any track in albumData received from VGMDB. Thus, this is a dangerous option, be careful

    performers: bool = False  # tag performers in the files
    arrangers: bool = False  # tag arrangers in the files
    composers: bool = False  # tag composers in the files
    lyricists: bool = False  # tag lyricists in the files

    english: bool = False  # Give Priority to English
    romaji: bool = False  # Give Priority to Romaji
    japanese: bool = False  # Give Priority to Japanese

    def configure(self):
        self.add_argument("root_dir")  # type: ignore
        self.add_argument("-r", "--recur")  # type: ignore
        self.add_argument("-y", "--yes")  # type: ignore

    def process_args(self):
        if self.folder_naming_template:
            try:
                TemplateResolver.validateTemplate(self.folder_naming_template)  # will raise exception if not valid
            except TemplateValidationException:
                escaped_folder_naming_template = self.folder_naming_template.replace("[", r"\[")
                get_console().print(f"[red]Provided folder naming template: [cyan bold]{escaped_folder_naming_template}[/] is invalid")
                exit(0)


def get_config_from_args() -> Config:
    """returns a Config instance after parsing the cli arguments and config present in config.json"""
    args = _get_args()
    config = get_config(**{k: v for k, v in args.items() if v})  # Removing None values first

    # if args["translate"]:
    #     config.keep_title = True # Choosing not to do this anymore
    if args["no_modify"]:
        config.tag = False
        config.rename = False
    if args["no_tag"]:
        config.tag = False
    if args["no_rename"]:
        config.rename = False
    if args["no_input"]:
        config.no_input = True
        config.yes = True

    if args["no_rename_folder"]:
        config.rename_folder = False
    if args["no_rename_files"]:
        config.rename_files = False
    if args["ksl"]:
        config.folder_naming_template = config.folder_naming_template_ksl  # easier to maintain if done like this

    if args["no_title"]:
        config.title = False
    if args["no_scans"]:
        config.scans_download = False
    if args["no_cover"]:
        config.album_cover = False
    if args["cover_overwrite"]:
        config.album_cover_overwrite = True

    if args["one_lang"]:
        config.all_lang = False
    if args["album_data_only"]:
        config.rename_files = False

    if args["performers"]:
        config.performers = True
    if args["arrangers"]:
        config.arrangers = True
    if args["lyricists"]:
        config.lyricists = True
    if args["composers"]:
        config.composers = True

    elif args["english"]:
        config.language_order = ["english", "translated", "romaji", "japanese", "other"]
    elif args["romaji"]:
        config.language_order = ["romaji", "english", "translated", "japanese", "other"]
    if args["japanese"]:
        config.language_order = ["japanese", "romaji", "translated", "english", "other"]

    return config


def _get_args() -> dict[str, Any]:
    """returns tuple of args combined from CLI and args derived from config.json file"""
    cli_args = _get_cli_args()
    file_args = _get_json_args()
    unexpected_args = set(file_args.keys()) - set(cli_args.keys())
    if unexpected_args:
        raise TypeError(f"unexpected argument in config.json: {', '.join(unexpected_args)}")
    cli_args.update(file_args)
    return cli_args


def _get_cli_args() -> dict[str, Any]:
    return CLIArgs().parse_args().as_dict()


def _get_json_args() -> dict[str, Any]:
    """use config.json in root directory to override args"""
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.abspath(os.path.join(current_directory, "..", "..", "..", "config.json"))
    if os.path.exists(config_file_path):
        get_console().log(f"[green bold] Reading config.json at {config_file_path}")
        with open(config_file_path, "r") as file:
            file_config = json.load(file)
            return file_config
    get_console().log(f"[red bold] Could not read config.json at {config_file_path}")
    return {}
