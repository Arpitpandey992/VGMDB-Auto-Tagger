#  VGMDB-Auto-Tagger
Python script to automatically tag an album using data fetched from VGMDB.info

## Some Important Requirements
* The music files must have proper `tracknumber` and `discnumber` tags for this to work.
* Tags like `artist`, `album artist` are not supported as this data is not present in VGMDB itself.
* This script works best for partially tagged albums, and it will fill in other details like `catalog`, `title`, `publisher`, etc. So it is best used in conjunction with other tagging tools, as it is very difficult to get `English` track titles and `catalog` using other tools.

## Usage
Clone the repository, then inside the directory:
```
usage: albumTagger.py [-h] [--id ID] [--search SEARCH] [--no-title] [--no-auth] [--yes] [--no-input] [--backup] [--no-scans] [--no-pics] [--pic-overwrite]
                      [--rename-folder] [--no-rename-folder] [--rename-files] [--no-rename-files] [--tag] [--no-tag] [--no-modify] [--japanese] [--english]
                      [--romaji]
                      folderPath

Automatically Tag Music folders using data from VGMDB.net

positional arguments:
  folderPath            Album directory path (Required Argument)

options:
  -h, --help            show this help message and exit
  --id ID, -i ID        Provide Album ID
  --search SEARCH, -s SEARCH
                        Provide Custom Search Term
  --no-title            Do not change the title of tracks
  --no-auth             Do not authenticate for downloading Scans
  --yes, -y             Skip Yes prompt, and when only 1 album comes up in search results
  --no-input            Go full auto mode, and only tag those albums where no user input is required!
  --backup, -b          Backup the albums before modifying
  --no-scans            Do not download Scans
  --no-pics             Do not embed album cover into files
  --pic-overwrite       overwrite album cover within files
  --rename-folder       Rename the containing folder
  --no-rename-folder    Do not Rename the containing folder?
  --rename-files        rename the files
  --no-rename-files     Do not rename the files
  --tag                 tag the files
  --no-tag              Do not tag the files
  --no-modify           Do not modify the files or folder in any way
  --japanese, -ja       Give Priority to Japanese
  --english, -en        Give Priority to English
  --romaji, -ro         Give Priority to Romaji


```

During picture grabbing stage, it is required to give username and password, since getting all scans require the client to be logged in. If you want to skip the login part and are okay with not grabbing all available scans, pass the --no-auth flag.

## Progress and Future Plans
- [X] Making the program more fail-safe and "trustable".
- [X] Adding support for FLAC.
- [X] Adding support for MP3.
- [X] Adding support for OGG.
- [ ] Adding support for M4A.
- [ ] Adding support for AAC.
- [ ] Integrating some other API (Like Musicbrainz) to get tags such as `artist`, `album artist`, etc.
- [ ] Adding a User Interface for easily using the script.
- [ ] Script for easily managing albums that were tagged once, by fetching data in a fully automatic fashion.
