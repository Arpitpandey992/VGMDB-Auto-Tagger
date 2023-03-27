import os
import argparse
import shutil
import json
from typing import Optional, Dict, List
from tabulate import tabulate


from Imports.flagsAndSettings import Flags, tableFormat, BACKUPFOLDER, APICALLRETRIES
from Utility.utilityFunctions import getAlbumDetails, yesNoUserInput, noYesUserInput, getBest, searchAlbum, fixDate, cleanSearchTerm

from Modules.Tag.tagFiles import tagFiles
from Modules.Rename.renameFiles import renameFiles
from Modules.Rename.renameFolder import renameFolder
from Utility.audioUtilityFunctions import getSearchTermAndDate, getAlbumTrackData, getFolderTrackData, doTracksAlign, getYearFromDate
from Modules.vgmdbrip.vgmdbrip import getPictures, getPicturesTheOldWay

from Types.albumData import AlbumData
from Types.search import SearchAlbumData
from Types.otherData import OtherData


def argumentParser() -> tuple[argparse.Namespace, Flags, str]:
    parser = argparse.ArgumentParser(description='Automatically Tag Music folders using data from VGMDB.net!')

    parser.add_argument('folderPath', type=str, help='Album directory path (Required Argument)')

    parser.add_argument('--id', '-i', type=str, default=None,
                        help='Provide Album ID')
    parser.add_argument('--search', '-s', type=str, default=None,
                        help='Provide Custom Search Term')

    parser.add_argument('--no-title', dest='no_title', action='store_true',
                        help='Do not change the title of tracks')
    parser.add_argument('--keep-title', dest='keep_title', action='store_true',
                        help='keep the current title as well, and add other available titles')
    parser.add_argument('--no-auth', dest='no_auth', action='store_true',
                        help='Do not authenticate for downloading Scans')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Skip Yes prompt, and when only 1 album comes up in search results')
    parser.add_argument('--no-input', dest='no_input', action='store_true',
                        help='Go full auto mode, and only tag those albums where no user input is required!')
    parser.add_argument('--backup', '-b', action='store_true',
                        help='Backup the albums before modifying')
    parser.add_argument('--no-scans', dest='no_scans', action='store_true',
                        help='Do not download Scans')
    parser.add_argument('--no-pics', dest='no_pics', action='store_true',
                        help='Do not embed album cover into files')
    parser.add_argument('--pic-overwrite', dest='pic_overwrite', action='store_true',
                        help='overwrite album cover within files')

    parser.add_argument('--rename-folder', dest='rename_folder', action='store_true',
                        help='Rename the containing folder')
    parser.add_argument('--no-rename-folder', dest='no_rename_folder', action='store_true',
                        help='Do not Rename the containing folder?')
    parser.add_argument('--rename-files', dest='rename_files', action='store_true',
                        help='rename the files')
    parser.add_argument('--no-rename-files', dest='no_rename_files', action='store_true',
                        help='Do not rename the files')
    parser.add_argument('--tag', dest='tag', action='store_true',
                        help='tag the files')
    parser.add_argument('--no-tag', dest='no_tag', action='store_true',
                        help='Do not tag the files')
    parser.add_argument('--no-modify', dest='no_modify', action='store_true',
                        help='Do not modify the files or folder in any way')
    parser.add_argument('--one-lang', dest='one_lang', action='store_true',
                        help='Only keep the best names')
    parser.add_argument('--translate', dest='translate', action='store_true',
                        help='Translate all text to english')

    parser.add_argument('--single', action='store_true',
                        help='enable this if there is only one track in the album')
    parser.add_argument('--performers', action='store_true',
                        help='tag performers in the files')
    parser.add_argument('--arrangers', action='store_true',
                        help='tag arrangers in the files')
    parser.add_argument('--composers', action='store_true',
                        help='tag composers in the files')
    parser.add_argument('--lyricists', action='store_true',
                        help='tag lyricists in the files')

    parser.add_argument('--japanese', '-ja', action='store_true',
                        help='Give Priority to Japanese')
    parser.add_argument('--english', '-en', action='store_true',
                        help='Give Priority to English')
    parser.add_argument('--romaji', '-ro', action='store_true',
                        help='Give Priority to Romaji')
    args = parser.parse_args()

    folderPath: str = args.folderPath

    while folderPath[-1] == '/':
        folderPath = folderPath[:-1]

    flags = Flags()
    if args.japanese:
        flags.languageOrder = ['japanese', 'romaji', 'english']
    elif args.english:
        flags.languageOrder = ['english', 'romaji', 'japanese']
    elif args.romaji:
        flags.languageOrder = ['romaji', 'english', 'japanese']

    if args.yes:
        flags.YES = True  # type: ignore
    if args.no_input:
        flags.NO_INPUT = True  # type: ignore
    if args.backup:
        flags.BACKUP = True  # type: ignore
    if args.rename_folder:
        flags.RENAME_FOLDER = True  # type: ignore
    if args.no_rename_folder:
        flags.RENAME_FOLDER = False  # type: ignore
    if args.rename_files:
        flags.RENAME_FILES = True  # type: ignore
    if args.no_rename_files:
        flags.RENAME_FILES = False  # type: ignore
    if args.tag:
        flags.TAG = True  # type: ignore
    if args.no_tag:
        flags.TAG = False  # type: ignore
    if args.no_title:
        flags.TITLE = False  # type: ignore
    if args.keep_title:
        flags.KEEP_TITLE = True  # type: ignore
    if args.one_lang:
        flags.ALL_LANG = False  # type: ignore
    if args.translate:
        flags.TRANSLATE = True  # type: ignore
        # When translating, it is better not to keep multiple names (keeping the original name as it is assumed to not be in english)
        flags.ALL_LANG = False  # type: ignore
        flags.KEEP_TITLE = True  # type: ignore

    if args.no_scans:
        flags.SCANS = False  # type: ignore
    if args.no_pics:
        flags.PICS = False  # type: ignore
    if args.pic_overwrite:
        flags.PIC_OVERWRITE = True  # type: ignore
    if args.no_auth:
        flags.NO_AUTH = True  # type: ignore

    if args.single or args.performers:
        flags.PERFORMERS = True  # type: ignore
    if args.single or args.arrangers:
        flags.ARRANGERS = True  # type: ignore
    if args.single or args.lyricists:
        flags.LYRICISTS = True  # type: ignore
    if args.single or args.composers:
        flags.COMPOSERS = True  # type: ignore

    if args.no_modify:
        flags.TAG = False  # type: ignore
        flags.RENAME_FOLDER = False  # type: ignore
        flags.RENAME_FILES = False  # type: ignore

    if flags.SEE_FLAGS:
        print(json.dumps(vars(flags), indent=4))
    return args, flags, folderPath


def tagAndRenameFiles(folderPath: str, albumID: str, flags: Flags) -> bool:
    print('\n', end='')
    print('Getting album Data')
    try:
        albumData: AlbumData = getAlbumDetails(albumID)
        if albumData is None:
            print('could not fetch album details, Please Try Again.')
            return False
    except Exception as e:
        print(e)
        return False

    albumData["vgmdb_link"] = albumData["vgmdb_link"].split("?")[0]
    # Setting crucial info for passing further
    albumData["album_id"] = albumID
    otherData: OtherData = {
        "flags": flags,
        "folder_path": folderPath
    }

    if 'catalog' in albumData and (albumData['catalog'] == 'N/A' or albumData['catalog'] == 'NA'):
        del albumData['catalog']

    if flags.CONFIRM:
        print(f'Link - {albumData["vgmdb_link"]}')
        print(f'Album - {getBest(albumData["names"], flags.languageOrder)}')
        if not yesNoUserInput():
            print('\n', end='')
            return False
        print('\n', end='')

    albumTrackData = getAlbumTrackData(albumData, otherData)
    folderTrackData = getFolderTrackData(folderPath)
    print('Done getting TrackData')
    print('\n', end='')
    print('\n', end='')

    if not doTracksAlign(albumTrackData, folderTrackData, flags):
        print('The tracks are not fully fitting the album data received from VGMDB!')
        if flags.NO_INPUT or not noYesUserInput():
            print('\n', end='')
            return False
    else:
        print('Tracks are perfectly aligning with the album data received from VGMDB!')
        if not flags.NO_INPUT and not flags.YES and not yesNoUserInput():
            print('\n', end='')
            return False

    print('\n', end='')
    print('\n', end='')

    # Fixing date in data to be in the form YYYY-MM-DD (MM and DD will be Zero if not present)
    albumData['release_date'] = fixDate(albumData['release_date'])

    if flags.BACKUP:
        try:
            destinationFolder = BACKUPFOLDER
            if not os.path.exists(destinationFolder):
                os.makedirs(destinationFolder)
            print(f'Backing Up {folderPath}...')
            print('\n', end='')
            backupFolder = os.path.join(
                destinationFolder, os.path.basename(folderPath))
            shutil.copytree(folderPath, backupFolder, dirs_exist_ok=False)
            print(f'Successfully copied {folderPath} to {backupFolder}')

        except Exception as e:
            print("Backup Couldn't Be Completed, but this probably means that this folder was already backed up, so it 'should' be safe ;)")
            print('error Message :', e)
            if not flags.NO_INPUT and not flags.YES and not yesNoUserInput():
                return False
        print('\n', end='')
        print('\n', end='')

    if flags.SCANS:
        print('Downloading Scans...')

        if not flags.NO_AUTH:
            # New Algorithm for downloading Scans -> All scans are downloaded, requires Authentication
            getPictures(folderPath, albumID)
        elif 'covers' in albumData:
            # Old algorithm for downloading -> no Authentication -> less covers available!
            getPicturesTheOldWay(albumData, otherData)

        print('Downloaded Available Pictures :)', end='\n\n')

    # Tagging
    if flags.TAG:
        print('Tagging files')
        print('\n', end='')
        tagFiles(albumTrackData, folderTrackData, albumData, otherData)
        print('Finished Tagging operation')
        print('\n', end='')
        print('\n', end='')
    # Renaming Files
    if flags.RENAME_FILES:
        print('Renaming Files')
        print('\n', end='')
        renameFiles(albumTrackData, folderTrackData, otherData)
        print('Finished Renaming Files')
        print('\n', end='')
        print('\n', end='')
    # Renaming Folder
    if flags.RENAME_FOLDER:
        print('Renaming Folder')
        print('\n', end='')
        renameFolder(albumData, otherData)

    return True


def getSearchInput() -> Optional[str]:
    print("Enter 'exit' to exit or give a new search term : ", end='')
    answer = input()
    if (answer.lower() == 'exit'):
        print('\n', end='')
        return None
    print('\n', end='')
    return answer


def findAlbumID(folderPath: str, searchTerm: Optional[str], searchYear: Optional[str], flags: Flags) -> Optional[str]:
    if flags.NO_INPUT and not searchTerm:
        return None
    folderName = os.path.basename(folderPath)
    print(f'Folder Name : {folderName}')
    if searchTerm is None:
        searchTerm = getSearchInput()
    # if searchTerm is still None -> user typed Exit
    if searchTerm is None:
        return None
    print(f'Searching for : {searchTerm}, Year = {searchYear}')
    print('\n', end='')
    albums = searchAlbum(searchTerm)
    if not albums:
        print("No results found!, Please change search term!")
        return findAlbumID(folderPath, None, None, flags)

    albumData: Dict[int, SearchAlbumData] = {}
    tableData = []
    serialNumber: int = 1
    for album in albums:
        albumID = album['link'].split('/')[1]
        albumLink: str = f"https://vgmdb.net/{album['link']}"
        albumTitle = getBest(album['titles'], flags.languageOrder)
        releaseDate = album['release_date']
        year = getYearFromDate(releaseDate)
        catalog = album['catalog']
        if not searchYear or searchYear == year:
            albumData[serialNumber] = {
                **album,
                "album_id": albumID,
                "release_year": year,
                "title": albumTitle
            }
            tableData.append((serialNumber, catalog, albumTitle, albumLink, year))
            serialNumber += 1
    if not tableData:
        # if we are here then that means we are getting some results but none are in the year provided
        return findAlbumID(folderPath, searchTerm, None, flags)
    print(tabulate(tableData,
                   headers=['S.No', 'Catalog', 'Title', 'Link', 'Year'],
                   maxcolwidths=52,
                   tablefmt=tableFormat,
                   colalign=('center', 'left', 'left', 'left', 'center')), end='\n\n')

    if (flags.NO_INPUT or flags.YES) and len(tableData) == 1:
        print('Continuing with this album!', end='\n\n')
        choice = '1'
    elif flags.NO_INPUT:
        return None
    else:
        print(f'Write another search term (exit allowed) or Choose Album Serial Number (1-{len(tableData)}) : ', end='')

        choice = input()
        if choice.lower() == 'exit':
            return None
        if choice == '':
            choice = '1'
        if not choice.isdigit() or int(choice) not in albumData:
            print('Invalid Choice, using that as search term!\n')
            return findAlbumID(folderPath, choice, None, flags)

    return albumData[int(choice)]['album_id']


def main():
    args, flags, folderPath = argumentParser()
    print(f"Working Folder : {folderPath}")
    albumID = args.id
    if albumID is None:
        searchTerm = args.search
        date = None
        if searchTerm is None:
            albumNameOrCatalog, date = getSearchTermAndDate(folderPath)
            if albumNameOrCatalog is None:
                print('Could not obtain either album name or catalog number from files in the directory, please provide custom search term!')
            searchTerm = cleanSearchTerm(albumNameOrCatalog)
        albumID = findAlbumID(folderPath, searchTerm, getYearFromDate(date), flags)
    if albumID:
        tagAndRenameFiles(folderPath, albumID, flags)
        print('Finished all <Possible> Operations')
    else:
        # if album-ID is still not found, script cannot do anything :(
        print(f'Operations failed at {folderPath}')


main()
