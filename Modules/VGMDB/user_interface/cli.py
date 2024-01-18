from curses.ascii import isdigit
import json
import os

# remove
import sys

from Modules.Print.utils import LINE_SEPARATOR, SUB_LINE_SEPARATOR

sys.path.append(os.getcwd())
# remove
import questionary
from typing import Callable

from Modules.Mutagen.mutagenWrapper import IAudioManager
from Modules.Mutagen.utils import extractYearFromDate
from Modules.Scan.Scanner import Scanner
from Modules.Tag import custom_tags
from Modules.Scan.models.local_album_data import LocalAlbumData
from Modules.Utils.general_utils import get_default_logger
from Modules.VGMDB.api import client
from Modules.VGMDB.user_interface.cli_args import CLIArgs
from Modules.Print import Table

logger = get_default_logger(__name__, "debug")


class CLI:
    def __init__(self):
        self.config = self._get_args().get_config()
        self.scanner = Scanner()

    def run(self):
        albums = self._scan_for_proper_albums(self.config.root_dir, self.config.recur)
        logger.info(LINE_SEPARATOR)
        logger.info(f"found {len(albums)} albums")
        for local_album_data in albums:
            logger.info(SUB_LINE_SEPARATOR)
            logger.info(f"operating on {local_album_data.album_folder_name}")
            logger.info(SUB_LINE_SEPARATOR)
            album_id = self._get_album_id(local_album_data)
            if not album_id:
                logger.error(f"could not find album id, skipping {local_album_data.album_folder_name}")
                continue
            logger.debug(f"for {local_album_data.album_folder_name}, album id: {album_id}")
            vgmdb_album_data = client.get_album_details(album_id)

    # Private Functions
    def _scan_for_proper_albums(self, root_dir: str, recur: bool) -> list[LocalAlbumData]:
        if recur:
            local_albums = self.scanner.scan_albums_recursively(root_dir)
        else:
            local_album = self.scanner.scan_album_in_folder_if_exists(root_dir)
            local_albums = [local_album] if local_album else []
        return local_albums

    def _get_album_id(self, local_album_data: LocalAlbumData) -> str | None:
        audio_manager = local_album_data.get_one_random_track().audio_manager
        vgmdb_id = audio_manager.getCustomTag(custom_tags.VGMDB_ID)
        if vgmdb_id and vgmdb_id[0].isdigit:
            logger.info("found album id in embedded tag")
            return vgmdb_id[0]

        # get search term
        search_term, reason = self.config.search, "provided search term"
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
        exit_ask, year_filter, no_year_filter = "exit", "yearFilter", "noYearFilter"
        while not album_found and not exit_flag:
            logger.info(f"searching for {search_term}")
            search_result = client.search_album(search_term)
            table_data = [(result.catalog, result.get_album_name(self.config.language_order), result.album_link, result.release_year) for result in search_result if (not year_filter_flag) or (year and result.release_year == year)]
            num_results = len(table_data)
            table_data = sorted(table_data, key=lambda x: x[1])
            columns = (
                Table.Column(header="Catalog", justify="left", style="cyan bold"),
                Table.Column(header="Title", justify="left", style="magenta"),
                Table.Column(header="Link", justify="left", style="green"),
                Table.Column(header="Year", justify="center", style="yellow"),
            )
            Table.tabulate(table_data, columns=columns, add_number_column=True, title=f"Search Results{f', year: {year}' if year and year_filter_flag else ' year: any'}")

            def is_choice_within_bounds(choice: str) -> bool | str:
                if not choice.isdigit():
                    return True
                return True if int(choice) >= 1 and int(choice) <= num_results else f"S.No. must be between 1 and {num_results}"

            if num_results == 0:
                choice = questionary.text(f"No results found, provide: search term | {exit_ask} | {no_year_filter if year and year_filter_flag else year_filter} -> ").ask()
            else:
                choice = questionary.text(
                    f"albums found: {num_results}, provide S.No. [1-{num_results}] | search term | {exit_ask} | {no_year_filter if year and year_filter_flag else year_filter} -> ",
                    default="1",
                    validate=is_choice_within_bounds,
                ).ask()
            if choice.lower() == no_year_filter.lower():
                year_filter_flag = False
            elif choice.lower() == year_filter.lower():
                year_filter_flag = True
            elif choice.lower() == exit_ask:
                exit_flag = True
            elif choice.isdigit():
                album_found = True
                album_id = os.path.basename(table_data[int(choice) - 1][2])
            else:
                search_term = choice
        return album_id

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

    def _get_args(self) -> CLIArgs:
        cli_args = CLIArgs().parse_args().as_dict()
        file_args = self._get_json_args()
        unexpected_args = set(file_args.keys()) - set(cli_args.keys())
        if unexpected_args:
            raise TypeError(f"unexpected argument in config.json: {', '.join(unexpected_args)}")
        cli_args.update(file_args)  # config file has higher priority
        return CLIArgs().from_dict(cli_args)

    def _get_json_args(self):
        """use config.json in root directory to override args"""
        config_file_path = "config.json"
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as file:
                file_config = json.load(file)
                return file_config
        return {}


if __name__ == "__main__":
    import sys

    sys.argv.append("/Users/arpit/Library/Custom/Music")
    sys.argv.append("--recur")
    cli_manager = CLI()
    cli_manager.run()
