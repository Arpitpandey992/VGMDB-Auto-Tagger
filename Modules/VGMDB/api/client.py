import requests
import sys
import os

sys.path.append(os.getcwd())

from Modules.Print.utils import SUB_LINE_SEPARATOR
from Modules.VGMDB.constants import APICALLRETRIES, USE_LOCAL_SERVER, VGMDB_INFO_BASE_URL
from Utility.generalUtils import get_default_logger
from Modules.VGMDB.models.vgmdb_album_data import VgmdbAlbumData
from Modules.VGMDB.models.search import SearchAlbum


logger = get_default_logger(__name__, "info")


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


def getRequest(url: str) -> dict | None:
    for _ in range(APICALLRETRIES):
        try:
            response = requests.get(url)
            if response.status_code >= 200 and response.status_code <= 299:
                return response.json()
        except Exception:
            pass
    return None


def getAlbumDetails(albumID: str) -> VgmdbAlbumData:
    def _clean_incoming_data(vgmdb_album_data: dict):
        if vgmdb_album_data["catalog"] == "N/A":
            vgmdb_album_data["catalog"] = None

        # Setting disc data in a format which is much faster to retrieve
        new_discs, disc_number = {}, 1
        for disc in vgmdb_album_data["discs"]:
            new_tracks, track_number = {}, 1
            for track in disc["tracks"]:
                new_tracks[track_number] = track
                track_number += 1
            disc["tracks"] = new_tracks
            new_discs[disc_number] = disc
            disc_number += 1
        vgmdb_album_data["discs"] = new_discs

    vgmdb_album_data = getRequest(f"{VGMDB_INFO_BASE_URL}/album/{albumID}")
    if not vgmdb_album_data:
        raise Exception(f"could not retrieve album details from vgmdb for albumID: {albumID}, most likely server error")
    _clean_incoming_data(vgmdb_album_data)

    return VgmdbAlbumData(**vgmdb_album_data, album_id=albumID)


def searchAlbum(albumName: str) -> list[SearchAlbum]:
    searchResult = getRequest(f"{VGMDB_INFO_BASE_URL}/search?q={albumName}")
    if not searchResult:
        raise Exception(f"could not search for {albumName} from vgmdb, most likely server error")
    return searchResult["results"]["albums"]


if __name__ == "__main__":
    print(getAlbumDetails("551").pprint() + "\n\n")
    print(getAlbumDetails("10052").pprint() + "\n\n")
    print(getAlbumDetails("19065").pprint() + "\n\n")
    albumSearchData = searchAlbum("Rewrite")
    print(albumSearchData)
