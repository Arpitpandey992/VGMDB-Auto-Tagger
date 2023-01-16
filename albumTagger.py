import os
import argparse
import shutil
import json

from tabulate import tabulate

from Imports.flagsAndSettings import *
from Utility.utilityFunctions import *

from Modules.Tag.tagFiles import tagFiles
from Modules.Rename.renameFiles import renameFiles
from Modules.Rename.renameFolder import renameFolder
from Utility.audioUtilityFunctions import getAlbumNameAndDate, getAlbumTrackData, getFolderTrackData, doTracksAlign, getYearFromDate
from Modules.vgmdbrip.vgmdbrip import getPictures, getPicturesTheOldWay


def argumentParser():
    parser = argparse.ArgumentParser(
        description='Automatically Tag Music folders using data from VGMDB.net')

    parser.add_argument('folderPath', help='Album directory path (Required Argument)')

    parser.add_argument('--ID', '-i', type=str, default=None,
                        help='Provide Album ID')
    parser.add_argument('--search', '-s', type=str, default=None,
                        help='Provide Custom Search Term')

    parser.add_argument('--no-title', dest='no_title', action='store_true',
                        help='Do not change the title of tracks')
    parser.add_argument('--no-auth', dest='no_auth', action='store_true',
                        help='Do not authenticate for downloading Scans')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Skip Yes prompt, and when only 1 album comes up in search results')
    parser.add_argument('--backup', '-b', action='store_true',
                        help='Backup the albums before modifying')
    parser.add_argument('--no-scans', dest='no_scans', action='store_true',
                        help='Do not download Scans')
    parser.add_argument('--no-pics', dest='no_pics', action='store_true',
                        help='Do not embed album cover into files')
    parser.add_argument('--pic-overwrite', dest='pic_overwrite', action='store_true',
                        help='overwrite album cover')

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

    parser.add_argument('--japanese', '-ja', action='store_true',
                        help='Give Priority to Japanese')
    parser.add_argument('--english', '-en', action='store_true',
                        help='Give Priority to English')
    parser.add_argument('--romaji', '-ro', action='store_true',
                        help='Give Priority to Romaji')
    args = parser.parse_args()

    folderPath = args.folderPath

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
    if args.no_scans:
        flags.SCANS = False  # type: ignore
    if args.no_pics:
        flags.PICS = False  # type: ignore
    if args.pic_overwrite:
        flags.PIC_OVERWRITE = True  # type: ignore
    if args.no_auth:
        flags.NO_AUTH = True  # type: ignore

    if args.no_modify:
        flags.TAG = False  # type: ignore
        flags.RENAME_FOLDER = False  # type: ignore
        flags.RENAME_FILES = False  # type: ignore

    if SEE_FLAGS:
        print(json.dumps(vars(flags), indent=4))
    return args, flags, folderPath


def tagAndRenameFiles(folderPath, albumID, flags: Flags):
    print('\n', end='')
    print('Getting album Data')
    try:
        data = getAlbumDetails(albumID)
        if data is None:
            print('Failed, Please Try Again.')
            return False
    except Exception as e:
        print('Failed, Please Try Again.')
        print(e)
        return False

    albumLink = data["vgmdb_link"]
    while albumLink and albumLink[-1] != '?':
        albumLink = albumLink[:-1]
    albumLink = albumLink[:-1]
    # Setting crucial info for passing further
    data['albumLink'] = albumLink
    data['folderPath'] = folderPath
    data['albumID'] = albumID
    data['flags'] = flags
    if 'catalog' in data and (data['catalog'] == 'N/A' or data['catalog'] == 'NA'):
        del data['catalog']

    if flags.CONFIRM:
        print(f'Link - {albumLink}')
        print(f'Album - {getBest(data["names"], flags.languageOrder)}')
        if not yesNoUserInput():
            print('\n', end='')
            return False
        print('\n', end='')

    albumTrackData = getAlbumTrackData(data, flags.languageOrder)
    folderTrackData = getFolderTrackData(folderPath)
    print('Done getting TrackData')
    print('\n', end='')
    print('\n', end='')

    if not doTracksAlign(albumTrackData, folderTrackData):
        print('The tracks are not fully fitting the album data received from VGMDB!')
        if not noYesUserInput():
            print('\n', end='')
            return False
    else:
        print('Tracks are perfectly aligning with the album data received from VGMDB!')
        if not flags.YES and not yesNoUserInput():
            print('\n', end='')
            return False

    print('\n', end='')
    print('\n', end='')

    # Fixing date in data to be in the form YYYY-MM-DD (MM and DD will be Zero if not present)
    data['release_date'] = fixDate(data['release_date'])

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
            if not flags.YES and not yesNoUserInput():
                return False
        print('\n', end='')
        print('\n', end='')

    if flags.SCANS:
        print('Downloading Scans...')

        if not flags.NO_AUTH:
            # New Algorithm for downloading Scans -> All scans are downloaded, requires Authentication
            getPictures(folderPath, albumID)
        elif 'covers' in data:
            # Old algorithm for downloading -> no Authentication -> less covers available!
            getPicturesTheOldWay(data)

        print('Downloaded Available Pictures :)', end='\n\n')

    # Tagging
    if flags.TAG:
        print('Tagging files')
        print('\n', end='')
        tagFiles(albumTrackData, folderTrackData, data)
        print('Finished Tagging operation')
        print('\n', end='')
        print('\n', end='')
    # Renaming Files
    if flags.RENAME_FILES:
        print('Renaming Files')
        print('\n', end='')
        renameFiles(albumTrackData, folderTrackData, data)
        print('Finished Renaming Files')
        print('\n', end='')
        print('\n', end='')
    # Renaming Folder
    if flags.RENAME_FOLDER:
        print('Renaming Folder')
        print('\n', end='')
        renameFolder(data)


def getSearchInput():
    print("Enter 'exit' to exit or give a new search term : ", end='')
    answer = input()
    if(answer.lower() == 'exit'):
        print('\n', end='')
        return None
    print('\n', end='')
    return answer


def findAlbumID(folderPath, searchTerm, searchYear, flags: Flags):
    folderName = os.path.basename(folderPath)
    print(f'Folder Name : {folderName}')
    if searchTerm is None:
        searchTerm = getSearchInput()
    if searchTerm is None:
        return None
    print(f'Searching for : {searchTerm}, Year = {searchYear}')
    print('\n', end='')
    data = searchAlbum(searchTerm)
    if data is None or not data['results']['albums']:
        print("No results found!, Please change search term!")
        return findAlbumID(folderPath, None, None, flags)

    albumData = {}
    tableData = []
    serialNumber = 1
    for album in data['results']['albums']:  # type:ignore
        albumID = album['link'].split('/')[1]
        albumLink = f"https://vgmdb.net/{album['link']}"
        albumTitle = getBest(album['titles'], flags.languageOrder)
        releaseDate = album['release_date']
        year = getYearFromDate(releaseDate)
        catalog = album['catalog']
        albumData[serialNumber] = {
            'Link': albumLink,
            'Title': albumTitle,
            'ID': albumID,
            'Date': releaseDate,
            'Year': year,
            'Catalog': catalog
        }
        if not searchYear or searchYear == year:
            tableData.append((serialNumber, catalog, albumTitle, albumLink, year))
        serialNumber += 1
    if not tableData:
        return None
    print(tabulate(tableData,
                   headers=['S.No', 'Catalog', 'Title', 'Link', 'Year'],
                   maxcolwidths=52,
                   tablefmt=tableFormat,
                   colalign=('center', 'left', 'left', 'left', 'center')), end='\n\n')

    if flags.YES and len(tableData) == 1:
        print('Continuing with this album!', end='\n\n')
        choice = '1'
    else:
        print(
            f'Write another search term (exit allowed) or Choose Album Serial Number (1-{len(tableData)}) : ', end='')

        choice = input()
        if choice.lower() == 'exit':
            return None
        if choice == '':
            choice = '1'
        if not choice.isdigit() or int(choice) not in albumData:
            print('Invalid Choice, using that as search term!\n')
            return findAlbumID(folderPath, choice, None, flags)

    return albumData[int(choice)]['ID']


def main():
    args, flags, folderPath = argumentParser()

    albumID = args.ID
    if albumID is None:
        searchTerm = args.search
        date = None
        if searchTerm is None:
            albumName, date = getAlbumNameAndDate(folderPath)
            if albumName is None:
                print('Could not obtain album name from files in the directory, please provide custom search term!')
            searchTerm = cleanSearchTerm(albumName)
        albumID = findAlbumID(folderPath, searchTerm, getYearFromDate(date), flags)
    # if album-ID is still not found, script cannot do anything :(

    if albumID is not None:
        tagAndRenameFiles(folderPath, albumID, flags)
        print('Finished all <Possible> Operations')
    else:
        print(f'Operations failed at {folderPath}')


if __name__ == '__main__':
    main()
