import time
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


if USE_LOCAL_SERVER:
    try:
        from Modules.VGMDB.api.vgmdb_info import run_server

        logger.info("starting vgmdb.info server")
        logger.debug(SUB_LINE_SEPARATOR)
        baseAddress = run_server()
        VGMDB_INFO_BASE_URL = baseAddress
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

logger.info(f"using {VGMDB_INFO_BASE_URL} for VGMDB API")


def get_request(url: str) -> dict | None:
    backoff_secs = 1
    for _ in range(APICALLRETRIES):
        try:
            response = requests.get(url)
            if response.status_code >= 200 and response.status_code <= 299:
                return response.json()
        except Exception as e:
            logger.info(f"error in getting response, retrying after {backoff_secs} seconds")
            logger.debug(f"error: {e}")
            time.sleep(backoff_secs)
            backoff_secs *= 2
    return None


def get_album_details(album_id: str) -> VgmdbAlbumData:
    url = urljoin(VGMDB_INFO_BASE_URL, f"album/{album_id}")
    vgmdb_album_data = get_request(url)
    if not vgmdb_album_data:
        raise Exception(f"could not retrieve album details from vgmdb for albumID: {album_id}, most likely server error")

    return VgmdbAlbumData(**vgmdb_album_data, album_id=album_id)


def search_album(search_term: str) -> list[SearchAlbum]:
    url = urljoin(VGMDB_INFO_BASE_URL, f"search?q={search_term}")
    search_result = get_request(url)
    if not search_result:
        raise Exception(f"could not search for {search_term} from vgmdb, most likely server error")
    return [SearchAlbum.model_validate(result) for result in search_result["results"]["albums"]]


if __name__ == "__main__":
    print(get_album_details("551").pprint() + "\n\n")
    print(get_album_details("10052").pprint() + "\n\n")
    print(get_album_details("19065").pprint() + "\n\n")
    albumSearchData = search_album("Rewrite")
    print(albumSearchData)
