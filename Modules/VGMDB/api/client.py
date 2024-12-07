import textwrap
import traceback
import requests
import time
from typing import Any
from urllib.parse import urljoin

# REMOVE
import os
import sys

sys.path.append(os.getcwd())
# REMOVE

from Modules.VGMDB.constants import APICALLRETRIES, USE_LOCAL_SERVER, VGMDB_INFO_BASE_URL
from Modules.Print.utils import get_panel, get_rich_console
from Modules.VGMDB.models.vgmdb_album_data import VgmdbAlbumData
from Modules.VGMDB.models.search import SearchAlbum


console = get_rich_console()


class VgmdbRequestException(requests.RequestException):
    def __init__(self, message: str):
        super().__init__(message)


class VgmdbClient:
    def __init__(self) -> None:
        self.vgmdb_info_base_url = VGMDB_INFO_BASE_URL
        if USE_LOCAL_SERVER:
            try:
                from Modules.VGMDB.api.vgmdb_info import run_vgmdb_info_server

                console.log("[magenta bold]starting vgmdb.info server locally")

                baseAddress = run_vgmdb_info_server()

                self.vgmdb_info_base_url = baseAddress
            except Exception as e:
                console.print(
                    get_panel(
                        "[bold red]"
                        + textwrap.dedent(
                            f"""
                        Could not run vgmdb.info server locally
                        Make sure that docker is installed, running and added to $PATH
                        error:
                        {e}
                        """
                        ).strip()
                    )
                )
                console.print(
                    get_panel(
                        "[bold red]"
                        + textwrap.dedent(
                            f"""
                        Stacktrace:
                        {traceback.format_exc()}
                        """
                        ).strip()
                    )
                )
        console.print(get_panel(f"[bold yellow]Using [blue]{self.vgmdb_info_base_url}[/] for VGMDB API"))

        self.album_cache: dict[str, VgmdbAlbumData] = {}
        self.search_cache: dict[str, list[SearchAlbum]] = {}

    def get_request(self, url: str) -> dict[str, Any] | Exception:
        backoff_secs = 1
        found_exception = Exception("empty exception")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
        for _ in range(APICALLRETRIES):
            try:
                response = requests.get(url, headers=headers)
                if response.status_code >= 200 and response.status_code <= 299:
                    return response.json()
            except Exception as e:
                console.log(f"[red]error in getting response, retrying after {backoff_secs} seconds")
                console.log(f"[red]error: {e}")
                found_exception = e
                time.sleep(backoff_secs)
                backoff_secs *= 2
        return found_exception

    def get_album_details(self, album_id: str) -> VgmdbAlbumData:
        if album_id in self.album_cache:
            return self.album_cache[album_id]

        url = urljoin(self.vgmdb_info_base_url, f"album/{album_id}")
        vgmdb_album_data = self.get_request(url)
        if isinstance(vgmdb_album_data, Exception):
            raise VgmdbRequestException(f"could not retrieve album details from vgmdb for albumID: {album_id}")

        self.album_cache[album_id] = VgmdbAlbumData(**vgmdb_album_data, album_id=album_id)
        return self.album_cache[album_id]

    def search_album(self, search_term: str | None) -> list[SearchAlbum]:
        if not search_term:
            search_term = ""
        cleaned_search_term = self._clean_search_term(search_term)
        if cleaned_search_term in self.search_cache:
            return self.search_cache[cleaned_search_term]

        url = urljoin(self.vgmdb_info_base_url, f"search?q={cleaned_search_term}")
        search_result = self.get_request(url)
        if isinstance(search_result, Exception):
            raise VgmdbRequestException(f"could not search for {cleaned_search_term} from vgmdb")
        self.search_cache[cleaned_search_term] = [SearchAlbum.model_validate(result) for result in search_result["results"]["albums"]]
        return self.search_cache[cleaned_search_term]

    def _clean_search_term(self, name: str) -> str:
        def isJapanese(ch: str) -> bool:
            return ord(ch) >= 0x4E00 and ord(ch) <= 0x9FFF

        def isChinese(ch: str) -> bool:
            return ord(ch) >= 0x3400 and ord(ch) <= 0x4DFF

        ans = ""
        for ch in name:
            if ch.isalnum() or ch == " " or isJapanese(ch) or isChinese(ch):
                ans += ch
            else:
                ans += " "
        return ans


if __name__ == "__main__":
    client = VgmdbClient()
    for i in range(2):
        print(client.get_album_details("551").pprint() + "\n\n")
        print(client.get_album_details("10052").pprint() + "\n\n")
        print(client.get_album_details("19065").pprint() + "\n\n")
        print(client.get_album_details("41676").pprint() + "\n\n")
        print(client.search_album("Rewrite"), end="\n\n")
