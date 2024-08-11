import os
import shutil
import traceback
import questionary
import concurrent.futures
from typing import Any, Callable

from Imports.config import Config
from Imports.constants import THREAD_EXECUTOR_NUM_THREADS
from unigen import IAudioManager
from Modules.Organize.organizer import Organizer
from Modules.Organize.models.organize_result import FolderOrganizeResult
from Modules.Print import table
from Modules.Print.utils import get_panel, get_rich_console, print_separator
from Modules.Scan.scanner import Scanner
from Modules.Scan.models.local_album_data import LocalAlbumData
from Modules.Tag import custom_tags
from Modules.Tag.tagger import Tagger
from Modules.Translate.translator import Translator
from Modules.Utils.general_utils import get_default_logger, ifNot, to_sentence_case, extractYearFromDate
from Modules.VGMDB.api.client import VgmdbClient
from Modules.VGMDB.models.vgmdb_album_data import Names, VgmdbAlbumData
from Modules.VGMDB.user_interface import constants
from Modules.VGMDB.constants import VGMDB_OFFICIAL_BASE_URL

logger = get_default_logger(__name__, "info")


class CLI:
    def __init__(self, config: Config):
        self.root_config = config
        self.scanner = Scanner()
        self.translator = Translator()
        if config.tag:
            self.vgmdb_client = VgmdbClient()
        self.console = get_rich_console()
        self.colors = {"red": "#f3aba8", "green": "#d3f5b3"}
        self.no_change = ""
        self.not_available = "(Not Available)"

    def run(self):
        albums = self._scan_for_proper_albums(self.root_config.root_dir, self.root_config.recur)
        self.console.log(f"Found {len(albums)} Albums")
        print_separator()
        for album in albums:
            self.console.print(f"[bright_magenta bold]Operating on {album.album_folder_name}")
            if self.root_config.backup:
                self.console.print(get_panel(f"[bold green]Backing Up"))
                self._backup_local_album(album)
            print_separator()
            try:
                local_album_config = self.root_config.model_copy()
                local_album_config.root_dir = album.album_folder_path
                self.operate(album, local_album_config)
                print_separator()
                self.console.log(f"[green]Successfully Finished All Oprations on {album.album_folder_name}")
                print_separator()
            except Exception as e:
                print_separator()
                self.console.log(f"[bright_red bold]Error Occurred: {type(e).__name__} -> {e}, skipping {album.album_folder_path}")
                traceback_info = traceback.format_exc()
                logger.debug(traceback_info)
                print_separator()

    def operate(self, local_album_data: LocalAlbumData, config: Config) -> None:
        """Operate on the album (tag, download scans, organize,...)"""
        if config.tag:
            try:
                tagged_properly = self.tag(local_album_data, config)
                if not tagged_properly:
                    config.yes = False
            except Exception as e:
                config.yes = False
                print_separator()
                self.console.log(f"[bright_red bold]Error While Tagging: {type(e).__name__} -> {e}, not Tagging {local_album_data.album_folder_name}")
                traceback_info = traceback.format_exc()
                logger.debug(traceback_info)
                print_separator()
        if config.organize:
            try:
                organized_properly = self.organize(local_album_data, config)
                if not organized_properly:
                    config.yes = False
            except Exception as e:
                config.yes = False
                print_separator()
                self.console.log(f"[bright_red bold]Error While Organizing: {type(e).__name__} -> {e}, not Organizing {local_album_data.album_folder_name}")
                print_separator()

    def tag(self, local_album_data: LocalAlbumData, config: Config) -> bool:
        self.console.print(get_panel("[bold green]Tagging Metadata"))
        self.console.log(f"Fetching Album ID")
        album_id = self._get_album_id(local_album_data, config)
        if not album_id:
            raise Exception(f"Could Not Find Album ID For Folder: {local_album_data.album_folder_path}")

        self.console.log(f"Fetching Album Data With Album ID: {album_id}")
        vgmdb_album_data = self.vgmdb_client.get_album_details(album_id)

        logger.debug("linking local album data with vgmdb album data")
        vgmdb_album_data.link_local_album_data(local_album_data)

        logger.debug("showing match and getting confirmation")
        instruction = self._confirm_before_proceeding_to_tag(vgmdb_album_data, config)
        if instruction == constants.choices.no:
            logger.debug("tagging cancelled by user")
            return False
        if instruction == constants.choices.go_back:
            config.year_search = ""
            return self.tag(local_album_data, config)

        if config.scans_download:
            print_separator()
            self.console.print("[bold green]Downloading Scans")
            vgmdb_album_data.download_scans(local_album_data.album_folder_path, no_auth=self.root_config.no_auth)
            print_separator()

        self.console.print("[bold green]Tagging Album")
        Tagger(local_album_data, vgmdb_album_data, config).tag_files()
        print_separator()
        return True

    def organize(self, local_album_data: LocalAlbumData, config: Config) -> bool:
        print_separator()
        self.console.print(get_panel("[bold green]Organizing"))
        organizer = Organizer(local_album_data, config)
        folder_organize_result = organizer.organize()
        instruction = self._confirm_before_proceeding_to_organize(folder_organize_result, config)
        if instruction == constants.choices.no:
            logger.debug("orgznization cancelled by user")
            return False
        elif instruction == constants.choices.edit_configs:
            return self.organize(local_album_data, config)
        organizer.commit_changes(folder_organize_result)
        return True

    # Private Functions
    def _confirm_before_proceeding_to_organize(self, folder_organize_result: FolderOrganizeResult, config: Config) -> constants.choices:
        all_good = self._find_and_show_match_for_organization(folder_organize_result, config) and folder_organize_result.no_unclean_files
        message = "Please review changes, there might be issues" if not all_good else "Everything seems fine, proceed?"
        if config.no_input:
            choice = constants.choices.yes.value if all_good else constants.choices.no.value
        else:
            choice = (
                questionary.select(
                    message,
                    choices=[option.value for option in constants.choices if option != constants.choices.go_back],
                    default=constants.choices.yes.value if all_good else constants.choices.no.value,
                    style=questionary.Style([("question", f"fg:{self.colors['green'] if all_good else self.colors['red']} bold"), ("highlighted", "fg:white bold"), ("selected", "fg:white")]),
                )
                .skip_if(config.yes and all_good, default=constants.choices.yes.value)
                .ask()
            )

        if config.yes and not all_good:
            config.yes = False

        if not choice:  # user cancelled
            return constants.choices.no

        if choice != constants.choices.edit_configs.value:
            return constants.choices.from_value(choice)

        choices = [questionary.Choice(flag_name, checked=config.get_dynamically(flag_value)) for flag_name, flag_value in constants.CONFIG_MAP_FOR_ORGANIZE.items()]
        config_enable = questionary.checkbox("Toggle Configurations:", choices=choices).ask()
        if config_enable is None:
            return constants.choices.no
        config_disable = [key for key in constants.CONFIG_MAP_FOR_ORGANIZE.keys() if key not in config_enable]
        for flag in config_enable:
            config.set_dynamically(constants.CONFIG_MAP_FOR_ORGANIZE[flag], True)
        for flag in config_disable:
            config.set_dynamically(constants.CONFIG_MAP_FOR_ORGANIZE[flag], False)

        return constants.choices.edit_configs

    def _find_and_show_match_for_organization(self, folder_organize_result: FolderOrganizeResult, config: Config) -> bool:
        table_data: list[tuple[str, str, str, str]] = [
            (
                result.old_name,
                ifNot(result.new_name, self.not_available) if result.new_name != result.old_name else self.no_change,
                ifNot(result.old_disc_folder_name, ""),
                ifNot(result.new_disc_folder_name, "") if result.new_disc_folder_name != result.old_disc_folder_name else self.no_change,
            )
            for result in folder_organize_result.file_organize_results
        ]
        all_good = True

        if config.rename_folder:
            new_folder_name = folder_organize_result.new_name
            folder_name_changed = folder_organize_result.new_name != folder_organize_result.old_name
            self.console.print(f"[bold green]Folder Rename:{' (No Change)' if not folder_name_changed else ''}")
            self.console.print(f"[bright_red]{folder_organize_result.old_name}[/bright_red]\n[bright_green]{new_folder_name}[/bright_green]\n")

            all_good = all_good and bool(folder_organize_result.new_name)

        if config.rename_files:
            sort_comparator: Callable[[Any], Any] = lambda x: (x[2], x[0], x[3], x[1])
            table_data = sorted(table_data, key=sort_comparator)

            columns = (
                table.Column(header="Old Name", justify="left", style="cyan"),
                table.Column(header="New Name (if Changed)", justify="left", style="magenta"),
                table.Column(header="Disc Name (Old)", justify="left", style="yellow"),
                table.Column(header="Disc Name (New, if Changed)", justify="left", style="green"),
            )
            if not config.no_input:
                table.tabulate(table_data, columns=columns, title=f"Organizing Result for Files (Blank Field Means No Change)")

            all_good = all_good and all(res.new_path for res in folder_organize_result.file_organize_results)

        return all_good

    def _confirm_before_proceeding_to_tag(self, vgmdb_album_data: VgmdbAlbumData, config: Config) -> constants.choices:
        is_perfect_match = self._find_and_show_match_for_tagging(vgmdb_album_data, config)
        if is_perfect_match:
            question = questionary.select(
                "Local Album Data is matching perfectly with VGMDB Album Data, Proceed?",
                choices=[option.value for option in constants.choices],
                default=constants.choices.yes.value,
                style=questionary.Style([("question", f"fg:{self.colors['green']} bold"), ("highlighted", "fg:white bold"), ("selected", "fg:white")]),
            ).skip_if(config.yes or config.no_input, default=constants.choices.yes.value)
        else:
            question = questionary.select(
                "Local Album Data is NOT matching perfectly with VGMDB Album Data, Proceed?",
                choices=[option.value for option in constants.choices],
                default=constants.choices.no.value,
                style=questionary.Style([("question", f"fg:{self.colors['red']} bold"), ("highlighted", "fg:white bold"), ("selected", "fg:white")]),
                pointer="❯",
            ).skip_if(config.no_input, default=constants.choices.no.value)

        if config.yes and not is_perfect_match:
            config.yes = False

        choice = question.ask()
        if not choice:  # user cancelled
            return constants.choices.no

        if choice != constants.choices.edit_configs.value:
            return constants.choices.from_value(choice)

        choices = [questionary.Choice(flag_name, checked=config.get_dynamically(flag_value)) for flag_name, flag_value in constants.CONFIG_MAP_FOR_TAG.items()]
        config_enable = questionary.checkbox("Toggle Configurations:", choices=choices).ask()
        if config_enable is None:
            return constants.choices.no
        config_disable = [key for key in constants.CONFIG_MAP_FOR_TAG.keys() if key not in config_enable]
        for flag in config_enable:
            config.set_dynamically(constants.CONFIG_MAP_FOR_TAG[flag], True)
        for flag in config_disable:
            config.set_dynamically(constants.CONFIG_MAP_FOR_TAG[flag], False)
        # if constants.REVERSE_CONFIG_MAP_FOR_TAG["translate"] in config_enable: # Not choosing to do this since now keep title means we append the new titles, hence here it would not change the primary title if turned on
        #     config.keep_title = True
        if constants.REVERSE_CONFIG_MAP_FOR_TAG["translate"] in config_disable:
            vgmdb_album_data.clear_names("translated")

        return self._confirm_before_proceeding_to_tag(vgmdb_album_data, config)

    def _find_and_show_match_for_tagging(self, vgmdb_album_data: VgmdbAlbumData, config: Config) -> bool:
        """Find the match between the two data we have, and returns whether the albums are perfectly matching or not"""
        if config.translate:
            self.console.log(f"[bold green]Translating Album Name and Track Names to languages: {', '.join(config.translation_language)}")
            num_threads = THREAD_EXECUTOR_NUM_THREADS
            with self.console.status(f"[bold green]Translating Album Name and Track Names With {num_threads} threads"):
                to_translate: list[Names] = [vgmdb_album_data.names] + [track.names for disc in vgmdb_album_data.discs.values() for track in disc.tracks.values()]
                translated_names = self._translate_names(to_translate, config, num_threads)
                for i, name_object in enumerate(to_translate):
                    name_object.add_names(translated_names[i], "translated")

        table_data: list[tuple[int | str, int | str, str, str]] = []
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
            if data[0] == constants.NULL_INT or data[1] == constants.NULL_INT:
                data = ("", "", *data[2:])
                table_data[i] = data

        columns = (
            table.Column(header="Disc", justify="center", style="bold"),
            table.Column(header="Track", justify="center", style="bold"),
            table.Column(header=f"Title{' [Translated]' if config.translate else ''}", justify="left", style="cyan"),
            table.Column(header="File Name", justify="left", style="magenta"),
        )
        if not config.no_input:
            table.tabulate(table_data, columns=columns, title=f"Album Name{' [Translated]' if config.translate else ''}: {vgmdb_album_data.names.get_highest_priority_name(config.language_order)}")
        is_perfect_match = all(col for row in table_data for col in row)  # perfect match only if nothing is "" or None
        return is_perfect_match

    def _get_album_id(self, local_album_data: LocalAlbumData, config: Config) -> str | None:
        audio_manager = local_album_data.get_one_sample_track().audio_manager
        vgmdb_id = audio_manager.getCustomTag(custom_tags.VGMDB_ID)
        if vgmdb_id and vgmdb_id[0].isdigit():
            self.console.log("Found Album ID in Embedded Tag")
            use_embedded_id = questionary.confirm(f"Use Embedded Album ID ({VGMDB_OFFICIAL_BASE_URL}/album/{vgmdb_id[0]})?").skip_if(config.yes, default=constants.choices.yes.value).ask()
            if use_embedded_id:
                return vgmdb_id[0]

        # get search term
        search_reason = "provided search term"
        if not config.search:
            config.search, search_reason = self._extract_search_term_from_audio_file(audio_manager)
        if not config.search:
            config.search, search_reason = local_album_data.album_folder_name, "folder name"
        if not config.search:
            return None
        logger.debug(f"using {search_reason} as search term")

        # get year for filtering search results
        if config.year_search is None:
            config.year_search = extractYearFromDate(audio_manager.getDate())

        # keep searching for album using interaction with the user
        album_id: str | None = None
        exit_ask, year_filter = "Exit", "Year"
        while not album_id:
            self.console.log(f"Searching For [bold cyan]{config.search}")
            search_result = self.vgmdb_client.search_album(config.search)

            table_data = [(result.catalog, result.get_album_name(config.language_order), result.album_link, result.release_year) for result in search_result if not config.year_search or result.release_year == config.year_search]
            num_results = len(table_data)
            get_second_key: Callable[[Any], Any] = lambda x: x[1]
            table_data = sorted(table_data, key=get_second_key)
            columns = (
                table.Column(header="Catalog", justify="left", style="cyan bold"),
                table.Column(header="Title", justify="left", style="magenta"),
                table.Column(header="Link", justify="left", style="green"),
                table.Column(header="Year", justify="center", style="yellow"),
            )

            if not config.no_input:
                table.tabulate(table_data, columns=columns, add_number_column=True, title=f"Search Results, Search Term: {config.search}{f', year: {config.year_search}' if config.year_search else ''}")

            def is_choice_within_bounds(choice: str) -> bool | str:
                if not choice:
                    return "Choice cannot be empty"
                if not choice.isdigit():
                    return True
                elif num_results == 0:
                    return "No results available, provide search term or exit"
                return True if int(choice) >= 1 and int(choice) <= num_results else f"S.No. must be {f'between 1 and {num_results}' if num_results > 1 else 'equal to 1'}"

            def is_year_valid(year: str) -> bool | str:
                if not year or (len(year) == 4 and year.isdigit()):
                    return True
                return "Year must contain exactly 4 Digits or be empty"

            if config.no_input:
                choice = "1" if num_results == 1 else None
            else:
                if num_results == 0:
                    choice = questionary.text(
                        f"No results found, provide: search term | {year_filter} | {exit_ask}:",
                        validate=is_choice_within_bounds,
                    ).ask()
                else:
                    choice = (
                        questionary.text(
                            f"Albums found: {num_results}, Provide S.No. [1-{num_results}] | Search Term | {year_filter} | {exit_ask}:",
                            default="1" if num_results == 1 else "",
                            validate=is_choice_within_bounds,
                        )
                        .skip_if(config.yes and num_results == 1, default="1")
                        .ask()
                    )
            if config.yes and num_results != 1:
                config.yes = False
            if choice is None or choice.lower() == exit_ask.lower():  # User pressed ctrl + c or wrote exit
                return None
            elif choice.lower() == year_filter.lower():
                choice = questionary.text(
                    "Provide Year to Filter (Leave Empty to Disable Filter):",
                    default=config.year_search if config.year_search else "",
                    validate=is_year_valid,
                ).ask()
                config.year_search = choice
            elif choice.isdigit():
                album_id = os.path.basename(table_data[int(choice) - 1][2])
            else:
                config.search = choice
                config.year_search = ""
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

            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            shutil.copytree(album_folder, backup_album_folder, dirs_exist_ok=False)
            self.console.print(f"[green]Successfully Backed up {album_folder} to {backup_album_folder}")
        except FileExistsError as e:
            self.console.log(f"[yellow]Backup Couldn't Be completed because folder already exists (most likely already backed up before)")
        except Exception as e:
            self.console.log(f"[bold bright_red]Error during backup: {e}")
            raise (e)

    def _translate_names(self, to_translate: list[Names], config: Config, num_threads: int) -> list[list[str]]:
        """Translates Names present in to_translate, Returns translated names (list) for every Name"""
        def translate(name_object: Names) -> list[str]:
            track_title = name_object.get_highest_priority_name([order for order in config.language_order if order != "translated"])  # don't wanna translate translated text ;)
            try:
                translated_names: list[str] = []
                for translate_language in config.translation_language:
                    translated_name = self.translator.translate(track_title, translate_language)
                    if translated_name and translated_name != track_title:
                        translated_names.append(to_sentence_case(translated_name))

                successfully_translated = len(translated_names) > 0
                if successfully_translated:
                    self.console.log(f"[green]Translated [cyan bold]{track_title}")
                else:
                    self.console.log(f"[yellow]No need to Translate [cyan bold]{track_title}")

                return translated_names
            except Exception as e:
                self.console.log(f"[red bold]Error in Translating [cyan bold]{track_title}[/cyan bold], error: {e}")
                return []

        tasks: list[Any] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            for name_object in to_translate:
                tasks.append(executor.submit(translate, name_object))

        concurrent.futures.wait(tasks)
        return [future.result() for future in tasks]
