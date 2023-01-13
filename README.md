#  VGMDB-Auto-Tagger
Python script to automatically tag an album using data fetched from VGMDB.info

## Some Important Requirements
* The music files must have proper `tracknumber` and `discnumber` tags for this to work.
* Tags like `artist`, `album artist` are not supported as this data is not present in VGMDB itself.
* This script works best for partially tagged albums, and it will fill in other details like `catalog`, `title`, `publisher`, etc. So it is best used in conjunction with other tagging tools, as it is very difficult to get `English` track titles and `catalog` using other tools.

## Usage
Clone the repository, then inside the directory:
```
usage: albumTagger.py [-h] [--ID ID] [--yes] [--search SEARCH] [--japanese] [--english] [folderPath]
positional arguments:
  folderPath            Flac directory path

options:
  -h, --help            show this help message and exit
  --ID ID, -i ID        Provide Album ID
  --yes, -y, -Y         Skip Yes prompt, and when only 1 album comes up in search results
  --search SEARCH, -s SEARCH, -S SEARCH
                        Provide Custom Search Term
  --japanese, -ja       Give Priority to Japanese (not Romaji)
  --english, -en        Give Priority to English
  
Default Tagging Language -> Romaji
```

During picture grabbing stage, it is required to give username and password, since getting all scans require the client to be logged in. If you want to skip the login part and are okay with not grabbing all available scans, Uncomment some portion in the source code.

## Plans For Future
- [X] Making the program more fail-safe and "trustable".
- [X] Adding full support for FLAC.
- [ ] Adding full support for MP3.
- [ ] Adding full support for M4A.
- [ ] Adding full support for AAC.
- [ ] Integrating some other API to get tags like `artist`, `album artist`, etc.
- [ ] Adding a User Interface for easily using the script.
