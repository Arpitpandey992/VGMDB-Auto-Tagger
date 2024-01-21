import time
from typing import Any
from urllib.parse import urljoin
import requests
import os

# remove
import sys

sys.path.append(os.getcwd())
# remove
from Modules.Print.utils import SUB_LINE_SEPARATOR
from Modules.VGMDB.constants import APICALLRETRIES, USE_LOCAL_SERVER, VGMDB_INFO_BASE_URL
from Modules.Utils.general_utils import get_default_logger
from Modules.VGMDB.models.vgmdb_album_data import VgmdbAlbumData
from Modules.VGMDB.models.search import SearchAlbum


logger = get_default_logger(__name__, "debug")


class VgmdbRequestException(requests.RequestException):
    def __init__(self, message: str):
        super().__init__(message)


vgmdb_info_base_url = VGMDB_INFO_BASE_URL
if USE_LOCAL_SERVER:
    try:
        from Modules.VGMDB.api.vgmdb_info import run_server

        logger.info("starting vgmdb.info server")
        logger.debug(SUB_LINE_SEPARATOR)
        baseAddress = run_server()
        vgmdb_info_base_url = baseAddress
        logger.debug(SUB_LINE_SEPARATOR)
    except Exception as e:
        logger.error(
            f"""
{SUB_LINE_SEPARATOR}
could not run local server
****make sure docker is installed and it's service is running in system****
{SUB_LINE_SEPARATOR}
error:
{e}
{SUB_LINE_SEPARATOR}
""".strip()
        )

logger.info(f"using {vgmdb_info_base_url} for VGMDB API")

album_cache: dict[str, VgmdbAlbumData] = {}
search_cache: dict[str, list[SearchAlbum]] = {}


def get_request(url: str) -> dict[str, Any] | Exception:
    backoff_secs = 1
    found_exception = Exception("empty exception")
    for _ in range(APICALLRETRIES):
        try:
            response = requests.get(url)
            if response.status_code >= 200 and response.status_code <= 299:
                return response.json()
        except Exception as e:
            logger.info(f"error in getting response, retrying after {backoff_secs} seconds")
            logger.debug(f"error: {e}")
            found_exception = e
            time.sleep(backoff_secs)
            backoff_secs *= 2
    return found_exception


def get_album_details(album_id: str) -> VgmdbAlbumData:
    global album_cache
    if album_id in album_cache:
        return album_cache[album_id]

    url = urljoin(vgmdb_info_base_url, f"album/{album_id}")
    vgmdb_album_data = get_request(url)
    if isinstance(vgmdb_album_data, Exception):
        raise VgmdbRequestException(f"could not retrieve album details from vgmdb for albumID: {album_id}")

    album_cache[album_id] = VgmdbAlbumData(**vgmdb_album_data, album_id=album_id)
    return album_cache[album_id]


def search_album(search_term: str) -> list[SearchAlbum]:
    global search_cache
    if search_term in search_cache:
        return search_cache[search_term]

    url = urljoin(vgmdb_info_base_url, f"search?q={search_term}")
    search_result = get_request(url)
    if isinstance(search_result, Exception):
        raise VgmdbRequestException(f"could not search for {search_term} from vgmdb")
    search_cache[search_term] = [SearchAlbum.model_validate(result) for result in search_result["results"]["albums"]]
    return search_cache[search_term]


if __name__ == "__main__":
    for i in range(2):
        print(get_album_details("551").pprint() + "\n\n")
        print(get_album_details("10052").pprint() + "\n\n")
        print(get_album_details("19065").pprint() + "\n\n")
        print(get_album_details("41676").pprint() + "\n\n")
        print(search_album("Rewrite"), end="\n\n")
