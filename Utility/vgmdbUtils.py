from Imports.flagsAndSettings import APICALLRETRIES
from Utility.generalUtils import get_default_logger
from Modules.vgmdb_info.docker_commands import run_server

import requests


from typing import Any, Optional

from Types.albumData import AlbumData
from Types.search import SearchAlbum

logger = get_default_logger(__name__, 'info')


USE_LOCAL_SERVER = True
baseUrl = "https://vgmdb.info"

if USE_LOCAL_SERVER:
    try:
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


def Request(url: str) -> Optional[dict[Any, Any]]:
    countLeft = APICALLRETRIES
    while countLeft > 0:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        countLeft -= 1
    return None


def getAlbumDetails(albumID: str) -> AlbumData:
    return Request(f'{baseUrl}/album/{albumID}')  # type: ignore


def searchAlbum(albumName: str) -> Optional[list[SearchAlbum]]:
    searchResult = Request(f'{baseUrl}/search?q={albumName}')
    if not searchResult:
        return None
    return searchResult['results']['albums']
