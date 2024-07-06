APICALLRETRIES = 5
USE_LOCAL_SERVER = True  # This is not working lately, so better to just up the service using "docker-compose up" after cloning "https://github.com/Arpitpandey992/vgmdb"
# VGMDB_INFO_BASE_URL = "https://vgmdb.info" # The website is also having some issue lately
VGMDB_INFO_BASE_URL = "http://localhost:5020/"  # The docker compose version is fixed to run on 5020 port
VGMDB_OFFICIAL_BASE_URL = "https://vgmdb.net"
