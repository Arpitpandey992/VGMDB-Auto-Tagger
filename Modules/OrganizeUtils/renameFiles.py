import math
import shutil
import os

from Utility.mutagenWrapper import AudioFactory, supportedExtensions
from Utility.utilityFunctions import getProperCount, cleanName
from Utility.audioUtilityFunctions import getOneAudioFile
from Modules.Tag.tagUtilityFunctions import standardizeDate

"""
Rename all files recursively or iteratively in a directory.
Change file names to {Track Number} - {Track Name}
"""


def renameFiles(folderPath):
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

            trackNumber = getProperCount(trackNumber, totalTracks)
            date = standardizeDate(audio.getDate())
            if date == "":
                date = standardizeDate(audio.getCustomTag('year'))
            date = date.replace('-', '.')
            year = date[:4] if len(date) >= 4 else ""
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
