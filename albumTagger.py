import os
import argparse
import shutil
import json

from tabulate import tabulate

from Modules.flagsAndSettings import *
from Modules.tagFiles import *
from Modules.renameFiles import *
from Modules.renameFolder import *
from Modules.vgmdbrip.vgmdbrip import getPictures

folderPath = "/home/arpit/Downloads/[2012.01.25] STEINS;GATE Future Gadget Compact Disc 8 Soundtrack II ˮEvent Horizonˮ [MFXT-0008EX]"


def argumentParser():
    global folderPath
    parser = argparse.ArgumentParser(
        description='Automatically Tag Music Albums!, Default Language -> Romaji')

    parser.add_argument('folderPath', nargs='?', help='Flac directory path')

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
                        help='overwrite album cover?')

    parser.add_argument('--rename-folder', dest='rename_folder', action='store_true',
                        help='Rename the containing folder?')
    parser.add_argument('--no-rename-folder', dest='no_rename_folder', action='store_true',
                        help='Rename the containing folder?')
    parser.add_argument('--rename-files', dest='rename_files', action='store_true',
                        help='Do not rename the files')
    parser.add_argument('--no-rename-files', dest='no_rename_files', action='store_true',
                        help='Do not rename the files')
    parser.add_argument('--tag', dest='tag', action='store_true',
                        help='Do not tag the files')
    parser.add_argument('--no-tag', dest='no_tag', action='store_true',
                        help='Do not tag the files')

    parser.add_argument('--japanese', '-ja', action='store_true',
                        help='Give Priority to Japanese (not Romaji)')
    parser.add_argument('--english', '-en', action='store_true',
                        help='Give Priority to English')
    args = parser.parse_args()

    if args.folderPath:
        folderPath = args.folderPath

    while folderPath[-1] == '/':
        folderPath = folderPath[:-1]
    flags = Flags()
    if args.japanese:
        flags.languages = ['ja', 'Japanese', 'ja-latn', 'Romaji', 'en', 'English',
                           'English (Apple Music)', 'English/German']
    elif args.english:
        flags.languages = ['en', 'English',
                           'English (Apple Music)', 'English/German', 'ja-latn', 'Romaji', 'ja', 'Japanese']

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

    if SEE_FLAGS:
        print(json.dumps(vars(flags), indent=4))
    return args, flags


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

    if flags.CONFIRM:
        print(f'Link - {albumLink}')
        print(f'Album - {getBest(data["names"], flags.languages)}')
        if not yesNoUserInput():
            print('\n', end='')
            return False
        print('\n', end='')

    albumTrackData = getAlbumTrackData(data, flags.languages)
    folderTrackData = getFolderTrackData(folderPath, flags.languages)
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
            frontPictureExists = False
            coverPath = os.path.join(data['folderPath'], 'Scans')
            if not os.path.exists(coverPath):
                os.makedirs(coverPath)
            for cover in data['covers']:
                downloadPicture(URL=cover['full'],
                                path=coverPath, name=cover['name'])
                if cover['name'].lower() == 'front' or cover['name'].lower == 'cover':
                    frontPictureExists = True
            if not frontPictureExists and 'picture_full' in data:
                downloadPicture(URL=data['picture_full'],
                                path=coverPath, name='Front')

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


def findAlbumID(folderPath, searchTerm, flags: Flags):
    if searchTerm is None:
        searchTerm = getSearchInput()
    if searchTerm is None:
        return None
    folderName = os.path.basename(folderPath)
    print(f'Folder Name : {folderName}')
    print(f'Searching for : {searchTerm}')
    print('\n', end='')
    data = searchAlbum(searchTerm)
    if data is None or not data['results']['albums']:
        print("No results found!, Please change search term!")
        return findAlbumID(folderPath, None, flags)

    if data is None:
        return None

    albumData = {}
    tableData = []
    serialNumber = 1
    for album in data['results']['albums']:  # type:ignore
        albumID = album['link'].split('/')[1]
        albumLink = f"https://vgmdb.net/{album['link']}"
        albumTitle = getBest(album['titles'], flags.languages)
        releaseDate = album['release_date']
        year = releaseDate[0:4] if len(releaseDate) >= 4 else 'NA'
        catalog = album['catalog']
        albumData[serialNumber] = {
            'Link': albumLink,
            'Title': albumTitle,
            'ID': albumID,
            'Date': releaseDate,
            'Year': year,
            'Catalog': catalog
        }
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
            return findAlbumID(folderPath, choice, flags)

    return albumData[int(choice)]['ID']


def main():

    args, flags = argumentParser()

    albumID = args.ID
    if albumID is None:
        searchTerm = args.search
        if searchTerm is None:
            searchTerm = cleanSearchTerm(getAlbumName(folderPath))
        albumID = findAlbumID(folderPath, searchTerm, flags)

    # if album-ID is still not found, script cannot do anything :(

    if albumID is not None:
        tagAndRenameFiles(folderPath, albumID, flags)
        print('Finished all <Possible> Operations')
    else:
        print(f'Operations failed at {folderPath}')


if __name__ == '__main__':
    main()
