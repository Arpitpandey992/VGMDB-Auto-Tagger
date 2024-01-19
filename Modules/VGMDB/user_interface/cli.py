import os
import json
import shutil

# remove
import sys

sys.path.append(os.getcwd())
# remove
import questionary

from typing import Callable

from Imports.config import Config, get_config
from Modules.Mutagen.mutagenWrapper import IAudioManager
from Modules.Mutagen.utils import extractYearFromDate
from Modules.Print import Table
from Modules.Print.utils import LINE_SEPARATOR, SUB_LINE_SEPARATOR
from Modules.Scan.Scanner import Scanner
from Modules.Scan.models.local_album_data import LocalAlbumData
from Modules.Tag import custom_tags
from Modules.Tag.tagger import Tagger
from Modules.Translate import translator
from Modules.Utils.general_utils import get_default_logger, ifNot, printAndMoveBack
from Modules.VGMDB.api import client
from Modules.VGMDB.models.vgmdb_album_data import VgmdbAlbumData
from Modules.VGMDB.user_interface import constants
from Modules.VGMDB.user_interface.cli_args import CLIArgs

logger = get_default_logger(__name__, "info")


"""
Implementing layering using call stack
getting root dir + scanning + for each album:  {layer 0}   [Not considering this for layering rn]
    getting album id (user input is considered) + fetch data  {layer 1} [No need to implement back, topmost layer]
        show match + ask for direction  {layer 2} [Flag change mech is implemented here]

ways to implement:
1) iterative stack based, with stack containing Callable functions, but the implementation will be very difficult to understand statically
2) simple recursive solution, this will require nesting functions inside function, need to follow code to understand
3) make a generic module for this layering functionality (can use some existing lib as well)
4) Since this is currently simply two layer module (and linear), we can use while loop inside while loop, but that's a bad design + no scope for adding layers

"""


class CLI:
    def __init__(self):
        cli_args = self._get_args()
        self.root_config = self.get_config_from_args(cli_args)
        self.scanner = Scanner()

    def run(self):
        albums = self._scan_for_proper_albums(self.root_config.root_dir, self.root_config.recur)
        logger.info(LINE_SEPARATOR)
        logger.info(f"found {len(albums)} albums")
        for album in albums:
            if self.root_config.backup:
                self._backup_local_album(album)
            logger.info(SUB_LINE_SEPARATOR)
            logger.info(f"operating on {album.album_folder_name}")
            logger.info(SUB_LINE_SEPARATOR)
            try:
                local_album_config = self.root_config.model_copy()
                local_album_config.root_dir = album.album_folder_path
                self.operate(album, local_album_config)
                logger.info(SUB_LINE_SEPARATOR)
                logger.info(f"successfully finished all oprations on {album.album_folder_name}")
                logger.info(SUB_LINE_SEPARATOR)
            except Exception as e:
                logger.info(SUB_LINE_SEPARATOR)
                logger.error(f"error occurred: {type(e).__name__} -> {e}, skipping {album.album_folder_path}")
                logger.info(SUB_LINE_SEPARATOR)

    def operate(self, local_album_data: LocalAlbumData, config: Config):
        logger.debug(f"fetching album id")
        album_id = self._get_album_id(local_album_data, config)
        if not album_id:
            raise Exception(f"could not find album id for folder: {local_album_data.album_folder_path}")

        logger.debug(f"fetching album data with album id: {album_id}")
        vgmdb_album_data = client.get_album_details(album_id)

        logger.debug("linking local album data with vgmdb album data")
        vgmdb_album_data.link_local_album_data(local_album_data)

        logger.debug("showing match and getting confirmation")
        instruction = self._confirm_before_proceeding(vgmdb_album_data, config)
        if instruction == constants.choices.no:
            logger.debug("operation cancelled by user")
            return
        if instruction == constants.choices.go_back:
            return self.operate(local_album_data, config)
        # we are good to go :)

        if config.tag:
            Tagger(local_album_data, vgmdb_album_data, config).tag_files()

    # Private Functions
    def _confirm_before_proceeding(self, vgmdb_album_data: VgmdbAlbumData, config: Config) -> constants.choices:
        is_perfect_match = self._find_and_show_match(vgmdb_album_data, config)
        if is_perfect_match:
            question = questionary.select(
                "Local Album Data is matching perfectly with VGMDB Album Data, Proceed?",
                choices=[option.value for option in constants.choices],
                default=constants.choices.yes.value,
            ).skip_if(config.yes, default=constants.choices.yes.value)
        else:
            question = questionary.select(
                "Local Album Data is NOT matching perfectly with VGMDB Album Data, Proceed?",
                choices=[option.value for option in constants.choices],
                default=constants.choices.no.value,
            ).skip_if(config.no_input, default=constants.choices.no.value)
        choice = question.ask()
        if not choice:  # user cancelled
            return constants.choices.no

        if choice != constants.choices.edit_configs.value:
            return constants.choices.from_value(choice)

        choices = [questionary.Choice(flag_name, checked=config.get_dynamically(flag_value)) for flag_name, flag_value in constants.CONFIG_MAP.items()]
        config_enable = questionary.checkbox("Toggle Configurations:", choices=choices).ask()
        if config_enable is None:
            return constants.choices.no
        config_disable = [key for key in constants.CONFIG_MAP.keys() if key not in config_enable]
        for flag in config_enable:
            config.set_dynamically(constants.CONFIG_MAP[flag], True)
        for flag in config_disable:
            config.set_dynamically(constants.CONFIG_MAP[flag], False)
        if constants.REVERSE_CONFIG_MAP["translate"] in config_disable:
            vgmdb_album_data.clear_names("translated")

        return self._confirm_before_proceeding(vgmdb_album_data, config)

    def _find_and_show_match(self, vgmdb_album_data: VgmdbAlbumData, config: Config) -> bool:
        """Find the match between the two data we have, and returns whether the albums are perfectly matching or not"""
        if config.translate:
            logger.info("translating track names")
            for disc_number, vgmdb_disc in vgmdb_album_data.discs.items():
                for track_number, vgmdb_track in vgmdb_disc.tracks.items():
                    track_title = vgmdb_track.names.get_highest_priority_name([order for order in config.language_order if order != "translated"])  # don't wanna translate translated text ;)
                    printAndMoveBack(f"translating {track_title}")
                    translated_names = []
                    for translate_language in config.translation_language:
                        translated_name = translator.translate(track_title, translate_language)
                        translated_names.append(translated_name) if translated_name else None
                    vgmdb_track.names.add_names(translated_names, "translated")
            printAndMoveBack("")
            logger.info("finished")

        table_data = []
        for disc_number, vgmdb_disc in vgmdb_album_data.discs.items():
            for track_number, vgmdb_track in vgmdb_disc.tracks.items():
                local_track = vgmdb_track.local_track
                table_data.append(
                    (
                        disc_number,
                        track_number,
                        vgmdb_track.names.get_highest_priority_name(config.language_order),
                        local_track.file_name if local_track else "",
                    )
                )

        for local_track in vgmdb_album_data.unmatched_local_tracks:
            table_data.append(
                (
                    ifNot(local_track.audio_manager.getDiscNumber(), constants.NULL_INT),
                    ifNot(local_track.audio_manager.getTrackNumber(), constants.NULL_INT),
                    "",
                    local_track.file_name,
                )
            )
        table_data.sort()
        for i, data in enumerate(table_data):
            if data[0] == constants.NULL_INT:
                data = ("", "", *data[2:])
                table_data[i] = data

        columns = (
            Table.Column(header="Disc", justify="center", style="bold"),
            Table.Column(header="Track", justify="center", style="bold"),
            Table.Column(header=f"Title{' [Translated]' if config.translate else ''}", justify="left", style="cyan"),
            Table.Column(header="File Name", justify="left", style="magenta"),
        )
        if not config.no_input:
            Table.tabulate(table_data, columns=columns, title=f"Data Match Between Details from VGMDB Album and Local Album")
        is_perfect_match = all(col for row in table_data for col in row)  # perfect match only if nothing is "" or None
        return is_perfect_match

    def _get_album_id(self, local_album_data: LocalAlbumData, config: Config) -> str | None:
        audio_manager = local_album_data.get_one_random_track().audio_manager
        vgmdb_id = audio_manager.getCustomTag(custom_tags.VGMDB_ID)
        if vgmdb_id and vgmdb_id[0].isdigit:
            logger.info("found album id in embedded tag")
            use_embedded_id = questionary.confirm("use embedded album id?").skip_if(config.yes, default=constants.choices.yes.value).ask()
            if use_embedded_id:
                return vgmdb_id[0]

        # get search term
        search_term, reason = config.search, "provided search term"
        if not search_term:
            search_term, reason = self._extract_search_term_from_audio_file(audio_manager)
        if not search_term:
            search_term, reason = local_album_data.album_folder_name, "folder name"
        if not search_term:
            return None
        logger.info(f"using {reason} as search term")

        # get year for filtering search results
        year = extractYearFromDate(audio_manager.getDate())

        # keep searching for album using interaction with the user
        album_found, exit_flag, album_id, year_filter_flag = False, False, None, True
        exit_ask, year_filter, no_year_filter = "Exit", "yearFilter", "noYearFilter"
        while not album_found and not exit_flag:
            logger.info(f"searching for {search_term}")
            search_result = client.search_album(search_term)

            table_data = [(result.catalog, result.get_album_name(config.language_order), result.album_link, result.release_year) for result in search_result if (not year_filter_flag) or (year and result.release_year == year)]
            num_results = len(table_data)
            table_data = sorted(table_data, key=lambda x: x[1])
            columns = (
                Table.Column(header="Catalog", justify="left", style="cyan bold"),
                Table.Column(header="Title", justify="left", style="magenta"),
                Table.Column(header="Link", justify="left", style="green"),
                Table.Column(header="Year", justify="center", style="yellow"),
            )

            if not config.no_input:
                Table.tabulate(table_data, columns=columns, add_number_column=True, title=f"Search Results{f', year: {year}' if year and year_filter_flag else ' year: any'}")

            def is_choice_within_bounds(choice: str) -> bool | str:
                if not choice:
                    return "Choice cannot be empty"
                if not choice.isdigit():
                    return True
                elif num_results == 0:
                    return "No results available, provide search term or exit"
                return True if int(choice) >= 1 and int(choice) <= num_results else f"S.No. must be {f'between 1 and {num_results}' if num_results > 1 else 'equal to 1'}"

            if num_results == 0:
                choice = (
                    questionary.text(
                        f"No results found, provide: search term | {exit_ask} | {no_year_filter if year and year_filter_flag else year_filter} -> ",
                        validate=is_choice_within_bounds,
                    )
                    .skip_if(config.no_input, default=None)
                    .ask()
                )
            else:
                choice = (
                    questionary.text(
                        f"Albums found: {num_results}, Provide S.No. [1-{num_results}] | Search Term | {exit_ask} | {no_year_filter if year and year_filter_flag else year_filter} -> ",
                        default="1" if num_results == 1 else "",
                        validate=is_choice_within_bounds,
                    )
                    .skip_if(config.yes and num_results == 1, default="1")
                    .ask()
                )
            if choice is None or (config.no_input and num_results):
                return None
            if choice.lower() == no_year_filter.lower():
                year_filter_flag = False
            elif choice.lower() == year_filter.lower():
                year_filter_flag = True
            elif choice.lower() == exit_ask.lower():
                exit_flag = True
            elif choice.isdigit():
                album_found = True
                album_id = os.path.basename(table_data[int(choice) - 1][2])
            else:
                config.search = choice
                search_term = choice
        return album_id

    def _scan_for_proper_albums(self, root_dir: str, recur: bool) -> list[LocalAlbumData]:
        if recur:
            local_albums = self.scanner.scan_albums_recursively(root_dir)
        else:
            local_album = self.scanner.scan_album_in_folder_if_exists(root_dir)
            local_albums = [local_album] if local_album else []
        return local_albums

    def _extract_search_term_from_audio_file(self, audio_manager: IAudioManager) -> tuple[str | None, str | None]:
        tag_functions: list[tuple[Callable[[], list[str]], str]] = [
            (audio_manager.getCatalog, "catalog number"),
            (audio_manager.getBarcode, "barcode"),
            (audio_manager.getAlbum, "album name"),
        ]
        for func, tag in tag_functions:
            value = func()
            if value:
                return value[0], tag
        return None, None

    def _backup_local_album(self, local_album_data: LocalAlbumData):
        try:
            backup_folder = self.root_config.backup_folder
            album_folder = local_album_data.album_folder_path
            backup_album_folder = os.path.join(backup_folder, os.path.basename(album_folder))
            logger.info(f"backing Up {album_folder}")

            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            shutil.copytree(album_folder, backup_album_folder, dirs_exist_ok=False)
            logger.info(f"successfully backed up {album_folder} to {backup_album_folder}")
        except Exception as e:
            logger.error("backup couldn't Be completed, but this probably means that this folder was already backed up, so it 'should' be safe ;)")
            logger.error(e)

    def _get_args(self) -> dict:
        """returns tuple of args combined from CLI and args derived from config.json file"""
        cli_args = CLIArgs().parse_args().as_dict()
        file_args = self._get_json_args()
        unexpected_args = set(file_args.keys()) - set(cli_args.keys())
        if unexpected_args:
            raise TypeError(f"unexpected argument in config.json: {', '.join(unexpected_args)}")
        cli_args.update(file_args)
        return cli_args

    def _get_json_args(self):
        """use config.json in root directory to override args"""
        config_file_path = "config.json"
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as file:
                file_config = json.load(file)
                return file_config
        return {}

    def get_config_from_args(self, args: dict) -> Config:
        config = get_config(**{k: v for k, v in args.items() if v})  # Removing None values first

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
            config.folder_naming_template = "{[{catalog}] }{albumname}{ [{date}]}{ [{format}]}"

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


if __name__ == "__main__":
    import sys

    sys.argv.append("/Users/arpit/Library/Custom/Music")
    sys.argv.append("--recur")
    cli_manager = CLI()
    cli_manager.run()
