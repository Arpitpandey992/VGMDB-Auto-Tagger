import os
import argparse
import shutil
from tabulate import tabulate

from flagsAndSettings import *
from tagFiles import *
from renameFiles import *


# languages to be probed from VGMDB in the given order of priority
languages = ['ja-latn', 'Romaji', 'en', 'English',
             'English (Apple Music)', 'ja', 'Japanese']


def tagAndRenameFiles(folderPath, albumID):
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
    data['albumLink'] = albumLink
    data['folderPath'] = folderPath
    if CONFIRM:
        print(f'Link - {albumLink}')
        print(f'Album - {getBest(data["names"], languages)}')
        if not yesNoUserInput():
            print('\n', end='')
            return False
        print('\n', end='')

    albumTrackData = getAlbumTrackData(data, languages)
    folderTrackData = getFolderTrackData(folderPath, languages)
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
        if not yesNoUserInput():
            print('\n', end='')
            return False

    print('\n', end='')
    print('\n', end='')
    if BACKUP:
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
            if not yesNoUserInput():
                return False
        print('\n', end='')
        print('\n', end='')

    # Tagging
    if TAG:
        print('Tagging files')
        print('\n', end='')
        tagFiles(albumTrackData, folderTrackData, data, languages)
        print('Finished Tagging operation')
        print('\n', end='')
        print('\n', end='')
    # Renaming
    if RENAME:
        print('Renaming Files and Folders')
        print('\n', end='')
        renameFiles(albumTrackData, folderTrackData, data, languages)
        print('Finished Renaming Operation')
        print('\n', end='')
        print('\n', end='')


def findAlbumID(folderPath, searchTerm):
    folderName = os.path.basename(folderPath)
    print(f'Folder Name : {folderName}')
    albumName = searchTerm
    if searchTerm is None:
        filePath = getOneAudioFile(folderPath)
        if filePath is None:
            print(
                'No Audio File Present in the directory to get album name, please provide custom search term!')
            print('\n', end='')
            print('\n', end='')
            return None

        audio = openMutagenFile(filePath)
        if 'album' not in audio or not audio['album']:
            print(
                'Audio file does not have an <album> tag!, please provide custom search term')
            print('\n', end='')
            print('\n', end='')
            return None
        albumName = audio["album"][0]
    print(f'Searching for : {albumName}')
    print('\n', end='')
    data = searchAlbum(albumName)
    if data is None or not data['results']['albums']:
        print("No results found!, Please change search term!")
        print("Enter 'exit' to exit or give a new search term : ", end='')
        answer = input()
        if(answer.lower() == 'exit'):
            print('\n', end='')
            return None
        return findAlbumID(folderPath, answer)

    albumData = {}
    tableData = []
    serialNumber = 1
    for album in data['results']['albums']:
        albumID = album['link'].split('/')[1]
        albumLink = f"https://vgmdb.net/{album['link']}"
        albumTitle = getBest(album['titles'], languages)
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
                   maxcolwidths=55,
                   tablefmt=tableFormat,
                   colalign=('center', 'left', 'left', 'left', 'center')), end='\n\n')
    print(
        f'Write another search term (exit allowed) or Choose Album Serial Number (1-{len(tableData)}) : ', end='')

    choice = input()
    if choice.lower() == 'exit':
        return None
    if choice == '':
        choice = '1'
    if not choice.isdigit() or int(choice) not in albumData:
        print('Invalid Choice, using that as search term!')
        return findAlbumID(folderPath, choice)

    return albumData[int(choice)]['ID']


def main():
    folderPath = "/home/arpit/Downloads/2009.05.05 [MJCD-0010] Vivid Colors -KEY tribute album- [M3-23]"
    parser = argparse.ArgumentParser(
        description='Automatically Tag Music Albums!, Default Language -> Romaji')
    parser.add_argument('folderPath', nargs='?', help='Flac directory path')
    parser.add_argument('--ID', '-i', type=str, default=None,
                        help='Provide Album ID')
    parser.add_argument('--search', '-s', '-S', type=str, default=None,
                        help='Provide Custom Search Term')
    parser.add_argument('--japanese', '-ja', action='store_true',
                        help='Give Priority to Japanese (not Romaji)')
    parser.add_argument('--english', '-en', action='store_true',
                        help='Give Priority to English')
    args = parser.parse_args()
    searchTerm = args.search

    if args.folderPath:
        folderPath = args.folderPath

    print('\n', end='')
    while folderPath[-1] == '/':
        folderPath = folderPath[:-1]

    global languages
    if args.japanese:
        languages = ['ja', 'Japanese', 'ja-latn', 'Romaji', 'en', 'English',
                     'English (Apple Music)']
    elif args.english:
        languages = ['en', 'English',
                     'English (Apple Music)', 'ja-latn', 'Romaji', 'ja', 'Japanese']
    albumID = args.ID
    if albumID is None:
        albumID = findAlbumID(folderPath, searchTerm)
    if albumID is not None:
        tagAndRenameFiles(folderPath, albumID)
        print('Finished all <Possible> Operations')
    else:
        print(f'Operations failed at {folderPath}')


if __name__ == '__main__':
    main()
