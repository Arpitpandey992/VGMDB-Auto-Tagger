import requests
from typing import Optional

from Utility.generalUtils import get_default_logger
from Modules.vgmdb_info.docker_commands import run_server
from Types.vgmdbAlbumData import VgmdbAlbumData
from Types.search import SearchAlbum


logger = get_default_logger(__name__, 'info')

APICALLRETRIES = 5
USE_LOCAL_SERVER = False
baseUrl = "https://vgmdb.info"

if USE_LOCAL_SERVER:
    try:
        logger.info("starting vgmdb.info server")
        logger.debug("-----------")
        baseAddress = run_server()
        baseUrl = baseAddress
        logger.debug("-----------")
    except Exception as e:
        logger.error(f'''
-----------
could not run local server
****make sure docker is installed and it's service is running in system****
-----------
error:
{e}
-----------
'''.strip())

logger.info(f'using {baseUrl} for VGMDB API')


def getRequest(url: str) -> Optional[dict]:
    countLeft = APICALLRETRIES
    while countLeft > 0:
        try:
            response = requests.get(url)
            if response.status_code >= 200 and response.status_code <= 299:
                return response.json()
        except Exception:
            pass
        countLeft -= 1
    return None


def getAlbumDetails(albumID: str) -> VgmdbAlbumData:
    vgmdb_album_data = getRequest(f'{baseUrl}/album/{albumID}')
    if not vgmdb_album_data:
        raise Exception(f"could not retrieve album details from vgmdb for albumID: {albumID}, most likely server error")
    _clean_incoming_data(vgmdb_album_data)
    return VgmdbAlbumData(**vgmdb_album_data, album_id=albumID)


def searchAlbum(albumName: str) -> list[SearchAlbum]:
    searchResult = getRequest(f'{baseUrl}/search?q={albumName}')
    if not searchResult:
        raise Exception(f"could not search for {albumName} from vgmdb, most likely server error")
    return searchResult['results']['albums']


def _clean_incoming_data(vgmdb_album_data: dict):
    if vgmdb_album_data["catalog"] == "N/A":
        vgmdb_album_data["catalog"] = None

    # # Setting disc data in a format which is much faster to retrieve
    # new_discs, disc_number = {}, 1
    # for disc in vgmdb_album_data["discs"]:
    #     new_tracks, track_number = {}, 1
    #     for track in disc["tracks"]:
    #         new_tracks[track_number] = track
    #         track_number += 1
    #     disc["tracks"] = new_tracks
    #     new_discs[disc_number] = disc
    #     disc_number += 1
    # vgmdb_album_data["discs"] = new_discs


if __name__ == "__main__":
    albumData = getAlbumDetails("551")
    print(albumData.discs)
    print('\n\n\n')
    albumSearchData = searchAlbum("rewrite")
    print(albumSearchData)
