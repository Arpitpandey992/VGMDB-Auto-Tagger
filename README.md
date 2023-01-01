# FLAC-auto-tag
Python script to automatically tag an album using data fetched from VGMDB.info

## Some Important Requirements
* The music files must have proper `tracknumber` and `discnumber` tags for this to work.
* Tags like `artist`, `album artist` are not supported as this data is not present in VGMDB itself.
* This script works best for partially tagged albums, and it will fill in other details like `catalog`, `title`, `publisher`, etc. So it is best used in conjunction with other tagging tools, as it is very difficult to get `English` track titles and `catalog` using other tools.

## Usage
Clone the repository and use : `python albumTagger.py <folderPath> <extraArguments>`
Language -> Romaji

positional arguments:
  folderPath            Flac directory path

options:
```
  -h, --help            show this help message and exit
  --ID ID, -i ID        Provide Album ID
  --search SEARCH, -s SEARCH, -S SEARCH
                        Provide Custom Search Term
  --japanese, -ja       Give Priority to Japanese (not Romaji)
  --english, -en        Give Priority to English
```


