from typing import Literal


APICALLRETRIES = 5
USE_LOCAL_SERVER = True  # Local server is started using docker. If set to false, it will use VGMDB_INFO_BASE_URL for fetching data

VGMDB_INFO_BASE_URL = "https://vgmdb.info"  # The website has been giving some issue lately

LOCAL_DOCKER_RUN_TYPES = Literal["docker", "docker-compose"]
# 'docker' runs the image: hufman/vgmdb:latest after pulling.
# 'docker-compose' runs the internal services independently. It clones https://github.com/Arpitpandey992/vgmdb and runs `docker compose up -d` using subprocess command
VGMDB_INFO_LOCAL_RUN_TYPE: LOCAL_DOCKER_RUN_TYPES = "docker-compose"  # recommended to just use docker-compose. Other options are not working lately
VGMDB_INFO_DOCKER_COMPOSER_BASE_URL = "http://localhost:5020/"  # The docker compose version is fixed to run on 5020 port

VGMDB_OFFICIAL_BASE_URL = "https://vgmdb.net"
