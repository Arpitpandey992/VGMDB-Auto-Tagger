from typing import Dict
from tabulate import tabulate
from Utility.audioUtils import getFolderTrackData, getOneAudioFile
from Utility.generalUtils import cleanName, fixDate, getProperCount
from Utility.mutagenWrapper import AudioFactory, supportedExtensions
from Imports.flagsAndSettings import tableFormat
import os


def countAudioFiles(folderTrackData: Dict[int, Dict[int, str]]) -> int:
    return sum([len(tracks) for _, tracks in folderTrackData.items()])


def renameAlbumFolder(folderPath, sameFolderName: bool = False):
    """Rename the folder which contains ONE album"""
    filePath = getOneAudioFile(folderPath)
    if not filePath:
        print('No Audio file in directory!, aborting')
        return
    audio = AudioFactory.buildAudioManager(filePath)
    if sameFolderName:
        albumName = os.path.basename(folderPath)
    else:
        albumName = audio.getAlbum()
        if albumName is None:
            print(f'No Album Name in {filePath}, aborting')
            return
    date = fixDate(audio.getDate())
    if not date:
        date = fixDate(audio.getCustomTag('year'))
    if date:
        date = date.replace('-', '.')
    catalog = audio.getCatalog()
    newFolderName = albumName
    if catalog and date:
        newFolderName = f'[{date}] {albumName} [{catalog}]'
        # newFolderName = f'[{catalog]}] {albumName} [{date}]'
    elif catalog:
        newFolderName = f'{albumName} [{catalog}]'
    elif date:
        newFolderName = f'[{date}] {albumName}'
    else:
        newFolderName = f'{albumName}'

    oldFolderName = os.path.basename(folderPath)
    newFolderName = cleanName(newFolderName)

    baseFolderPath = os.path.dirname(folderPath)
    newFolderPath = os.path.join(baseFolderPath, newFolderName)
    if (oldFolderName != newFolderName):
        if os.path.exists(newFolderPath):
            print(f'{newFolderName} Exists, cannot rename {oldFolderName}')
        else:
            os.rename(folderPath, newFolderPath)
            print(f'Successfully Renamed {oldFolderName} to {newFolderName}')


def renameAlbumFiles(folderPath: str, noMove: bool = False, verbose: bool = False):
    """Rename all files present inside a directory which contains files corresponding to ONE album only"""
    folderTrackData = getFolderTrackData(folderPath)
    audioFilesCount = countAudioFiles(folderTrackData)
    isSingle = audioFilesCount == 1
    totalDiscs = len(folderTrackData)

    tableData = []
    for discNumber, tracks in folderTrackData.items():
        totalTracks = len(tracks)
        for trackNumber, filePath in tracks.items():
            fullFileName = os.path.basename(filePath)
            fileName, extension = os.path.splitext(fullFileName)

            audio = AudioFactory.buildAudioManager(filePath)
            title = audio.getTitle()
            if not title:
                print(f'Title not Present in file : {fileName} Skipped!')
                continue

            trackNumberStr = getProperCount(trackNumber, totalTracks)
            discNumberStr = getProperCount(discNumber, totalDiscs)

            oldName = fileName

            if isSingle:
                newName = cleanName(f"{title}{extension}")
            else:
                newName = cleanName(f"{trackNumberStr} - {title}{extension}")
            discName = audio.getDiscName()

            if discName:
                discFolderName = f'Disc {discNumber} - {discName}'
            else:
                discFolderName = f'Disc {discNumber}'

            if totalDiscs == 1 or noMove:
                discFolderName = ''
            discFolderPath = os.path.join(folderPath, discFolderName)
            if not os.path.exists(discFolderPath):
                os.makedirs(discFolderPath)
            newFilePath = os.path.join(discFolderPath, newName)
            if filePath != newFilePath:
                try:
                    if os.path.exists(newFilePath):
                        print(f'{newFilePath} Exists, cannot rename {fileName}')
                    else:
                        os.rename(filePath, newFilePath)
                        tableData.append((
                            discNumberStr,
                            trackNumberStr,
                            oldName,
                            os.path.join(discFolderName, newName)
                        ))

                except Exception as e:
                    print(f'Cannot rename {fileName}')
                    print(e)

    if verbose and tableData:
        print('Files Renamed as Follows\n')
        tableData.sort()
        print(
            tabulate(
                tableData,
                headers=['Disc', 'Track', 'Old Name', 'New Name'],
                colalign=('center', 'center', 'left', 'left'),
                maxcolwidths=53, tablefmt=tableFormat
            ),
            end='\n\n'
        )


def renameFiles(folderPath):
    """
    Rename all files recursively or iteratively in a directory.
    Change file names to {Track Number} - {Track Name}
    """
    for root, dirs, files in os.walk(folderPath):
        for file in sorted(files):
            _, extension = os.path.splitext(file)
            if extension.lower() not in supportedExtensions:
                print(f"{file} has unsupported extension ({extension})")
                continue
            filePath = os.path.join(root, file)
            audio = AudioFactory.buildAudioManager(filePath)

            title = audio.getTitle()
            if title is None:
                print(f'Title not present in {file}, Skipping!')
                continue
            trackNumber = audio.getTrackNumber()
            totalTracks = audio.getTotalTracks()
            artist = audio.getArtist()
            if totalTracks is None:
                totalTracks = '99'
            if not trackNumber:
                trackNumber = "1"
            trackNumber = getProperCount(trackNumber, totalTracks)
            date = fixDate(audio.getDate())
            if not date:
                date = fixDate(audio.getCustomTag('year'))
            if date:
                date = date.replace('-', '.')
            year = date[:4] if date and len(date) >= 4 else ""
            oldName = file
            names = {
                # For Albums
                1: f"{trackNumber} - {title}{extension}" if trackNumber is not None else f"{title}{extension}",
                # For Single Tracks:
                2: f"{artist} - {title}{extension}" if artist is not None else f"{title}{extension}",
                3: f"{title}{extension}",
                4: f"[{date}] {title}{extension}",
                5: f"[{year}] {title}{extension}"
            }
            albumTrackName, singleTrackName = 1, 3

            # Change the naming template here :
            isSingle = int(totalTracks) == 1
            nameChoice = singleTrackName if isSingle else albumTrackName

            newName = cleanName(names[nameChoice])

            newFilePath = os.path.join(root, newName)
            if oldName != newName:
                try:
                    if os.path.exists(newFilePath):
                        print(f'{newFilePath} Exists, cannot rename {file}')
                    else:
                        os.rename(filePath, newFilePath)
                        print(f'Renamed {oldName} to {newName}')
                except Exception as e:
                    print(f'Cannot rename {file}')
                    print(e)
    print("\ndone rename operation")


def organizeAlbum(folderPath, sameFolderName: bool = False):
    print(f'Organizing Album : {os.path.basename(folderPath)}')
    renameAlbumFiles(folderPath, verbose=True)
    renameAlbumFolder(folderPath, sameFolderName)
    print(f'{os.path.basename(folderPath)} Organized!')
    print('\n', end='')
