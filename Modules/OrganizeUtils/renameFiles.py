import math
import shutil
import os

from Utility.mutagenWrapper import AudioFactory, supportedExtensions
from Utility.utilityFunctions import getProperCount, cleanName
from Utility.audioUtilityFunctions import getOneAudioFile

"""
Rename all files recursively or iteratively in a directory.
Change file names to {Track Number} - {Track Name}
"""


def renameFiles(folderPath):
    for root, dirs, files in os.walk(folderPath):
        for file in sorted(files):
            _, extension = os.path.splitext(file)
            if extension.lower() not in supportedExtensions:
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

            trackNumber = getProperCount(trackNumber, totalTracks)

            oldName = file
            names = {
                1: f"{trackNumber} - {title}{extension}" if trackNumber is not None else f"{title}{extension}",
                2: f"{artist} - {title}{extension}" if artist is not None else f"{title}{extension}",
                3: f"{title}{extension}",
            }
            # Change the naming template here :
            nameChoice = 1
            newName = cleanName(names[nameChoice])

            newFilePath = os.path.join(root, newName)
            try:
                if os.path.exists(newFilePath):
                    print(f'{newFilePath} Exists, cannot rename {file}')
                elif oldName != newName:
                    os.rename(filePath, newFilePath)
                    print(f'Renamed {oldName} to {newName}')
            except Exception as e:
                print(f'Cannot rename {file}')
                print(e)
    print('\n', end='')
