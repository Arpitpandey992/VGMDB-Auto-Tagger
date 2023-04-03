import os
from Imports.flagsAndSettings import *
from Utility.generalUtils import Request

# Work in progress, trying to decouple the data fetching code to allow the easy integration of other APIs like musicbrainz (for artist names, and other stuff)


def getAlbumDetails(albumID):
    return Request(f'https://vgmdb.info/album/{albumID}')


def searchAlbum(albumName):
    return Request(f'https://vgmdb.info/search?q={albumName}')


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
        if not searchYear or searchYear == year:
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
            return findAlbumID(folderPath, choice, None, flags)

    return albumData[int(choice)]['ID']


def fetchFromVGMDB():
