# VGMDB-Auto-Tagger

Python script to automatically tag an album using data fetched from VGMDB.info

This project uses api from [hufman VGMDB.info](https://github.com/hufman/vgmdb). Respect+

## Some Important Requirements

- The music files must have proper `tracknumber` and `discnumber` tags for this to work.
- Tags like `artist`, `album artist` are not supported as this data is not present in VGMDB itself.
- This script works best for partially tagged albums, and it will fill in other details like `catalog`, `title`, `publisher`, etc. So it is best used in conjunction with other tagging tools, as it is very difficult to get `English` track titles and `catalog` using other tools.
- During picture grabbing stage, it is required to give username and password, since getting all scans require the client to be logged in. If you want to skip the login part and are okay with not grabbing all available scans, pass the --no-auth flag.
- If using the translate command, make sure to have translate-shell installed in your system, with it being added to path. Basically, 'trans <text>' should work. Get it <a href="https://github.com/soimort/translate-shell">Here</a>
- Running this requires python3.11, make sure to use a virtual environment

### Last updated to work with: `python v3.12`

## Installing Dependencies

### Clone the repository and create a virtual environment

```
git clone https://github.com/Arpitpandey992/VGMDB-Auto-Tagger.git
cd VGMDB-Auto-Tagger
python -m venv .venv
```

### Source into the created virtual environment

- bash shell: `source .venv/bin/activate`
- fish shell: `source .venv/bin/activate.fish`
- windows powershell: `.\.venv\Scripts\activate.ps1`
- windows cmd: `.\.venv\Scripts\activate.bat`

### Install dependencies

`pip install -r requirements.txt`

The requirements file is automatically generated using `pip-tools`.

For adding a new dependency:

- Add new dependency in `requirements.in` file, then run:
  ```
  pip install pip-tools
  pip-compile --upgrade
  pip-sync
  ```

## Usage

`python album_tagger.py <path_to_single_album_containing_folder>`

`python album_tagger.py -r <path_to_music_directory_containing_multiple_albums>`

There are various options we can pass to the script. use `python album_tagger.py --help` for more information.

```
python album_tagger.py [-r] [--id ID] [--search SEARCH] [-y] [--no_input] [--backup] [--backup_folder BACKUP_FOLDER]
                       [--no_auth] [--no_tag] [--no_rename] [--no_modify] [--no_rename_folder] [--no_rename_files]
                       [--same_folder_name] [--folder_naming_template FOLDER_NAMING_TEMPLATE] [--ksl] [--no_title]
                       [--keep_title] [--no_scans] [--no_cover] [--cover_overwrite] [--one_lang] [--translate]
                       [--album_data_only] [--performers] [--arrangers] [--composers] [--lyricists] [--english]
                       [--romaji] [--japanese] [-h]
                       root_dir

Automatically Tag Local Albums using Album Data from VGMDB.net!

positional arguments:
  root_dir              (str, required) Album root directory (Required Argument)

options:
  -r, --recur           (bool, default=False) recursively check the directory for albums
  --id ID               (str | None, default=None) Provide Album ID to avoid searching for the album
  --search SEARCH       (str | None, default=None) Provide Custom Search Term
  -y, --yes             (bool, default=False) Skip Yes prompt, and when only 1 album comes up in search results
  --no_input            (bool, default=False) Go full auto mode, and only tag those albums where no user input is
                        required!
  --backup              (bool, default=False) Backup the albums before modifying
  --backup_folder BACKUP_FOLDER
                        (str, default=~/Music/Backups) folder to backup the albums to before modification
  --no_auth             (bool, default=False) Do not authenticate for downloading Scans
  --no_tag              (bool, default=False) Do not tag the files
  --no_rename           (bool, default=False) Do not rename or move anything
  --no_modify           (bool, default=False) Do not tag or rename, for searching and testing
  --no_rename_folder    (bool, default=False) Do not Rename the containing folder
  --no_rename_files     (bool, default=False) Do not rename the files
  --same_folder_name    (bool, default=False) While renaming the folder, use the current folder name instead of
                        getting it from album name
  --folder_naming_template FOLDER_NAMING_TEMPLATE
                        (str | None, default=None) Give a folder naming template like "{[{catalog}] }{albumname}{
                        [{date}]}"
  --ksl                 (bool, default=False) for KSL folder, (custom setting), keep catalog first in naming
  --no_title            (bool, default=False) Do not touch track titles
  --keep_title          (bool, default=False) Keep the current title and add other available titles
  --no_scans            (bool, default=False) Do not download Scans
  --no_cover            (bool, default=False) Do not embed album cover into files
  --cover_overwrite     (bool, default=False) Overwrite album cover within files
  --one_lang            (bool, default=False) For tags with multiple values, only keep the highest priority one
  --translate           (bool, default=False) Translate all text to English and Romaji
  --album_data_only     (bool, default=False) Only tag album specific details to ALL files in the folder, this option
                        will tag those files as well which are not matching with any track in albumData received from
                        VGMDB. Thus, this is a dangerous option, be careful
  --performers          (bool, default=False) tag performers in the files
  --arrangers           (bool, default=False) tag arrangers in the files
  --composers           (bool, default=False) tag composers in the files
  --lyricists           (bool, default=False) tag lyricists in the files
  --english             (bool, default=False) Give Priority to English
  --romaji              (bool, default=False) Give Priority to Romaji
  --japanese            (bool, default=False) Give Priority to Japanese
  -h, --help            show this help message and exit
```

### For providing naming template in CLI argument

we have variables like `catalog` `foldername` `date` `albumname` `barcode`

in template, anything written inside curly braces is evaluated as a variable, and if anything inside the curly brace evaluates to false, then it evaluates to blank character.
evaluating to false means that the key written inside the curly brace was valid, but it did not exist in the file.

for example, consider naming template : `{[{catalog}] }{[{albumname}]}`

here, we have catalog inside bracket and the entire [catalog] block inside another bracket.

This means that if file contains a `catalog` tag, then the name will be like: `[<catalog>] [<albumname>]`

otherwise, it will be like `[<albumname>]`

note that albumname will also be evaluated in a similar way here. Also, note that since square brackets are put inside another curly brackets, they only appear if the variable in the innermost layer is available. This is desirable because:

consider naming template like: `[{catalog}] [{albumname}]`

this will work fine when both of these variables are present, but if catalog is not present, then the name will evaluate to: `[] [<albumname>]` which is not desirable

## Progress and Future Plans

- [x] Making the program more fail-safe and "trustable".
- [x] Adding support for FLAC.
- [x] Adding support for MP3 and WAV.
- [x] Adding support for OGG and OPUS.
- [x] Adding support for M4A.
- [ ] Integrating some other API (Like Musicbrainz) to get tags such as `artist`, `album artist`, etc.
- [ ] Adding a User Interface for easily using the script.
- [ ] Script for easily managing albums that were tagged once, by fetching data in a fully automatic fashion.
