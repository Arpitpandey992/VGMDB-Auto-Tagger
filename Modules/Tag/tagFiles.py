import os
from tabulate import tabulate
from typing import Dict
from Imports.flagsAndSettings import tableFormat
from Types.albumData import AlbumData, TrackData
from Types.otherData import OtherData
from Utility.utilityFunctions import getBest
from Modules.Tag.tagUtilityFunctions import tagAudioFile
from Utility.mutagenWrapper import supportedExtensions


def tagFiles(albumTrackData: Dict[int, Dict[int, Dict[str, str]]],
             folderTrackData: Dict[int, Dict[int, str]],
             albumData: AlbumData,
             otherData: OtherData):
    flags = otherData.get('flags')
    totalDiscs = len(albumTrackData)

    tableData = []
    for discNumber, tracks in albumTrackData.items():

        totalTracks = len(tracks)

        for trackNumber, trackTitles in tracks.items():
            if discNumber not in folderTrackData or trackNumber not in folderTrackData[discNumber]:
                continue

            filePath = folderTrackData[discNumber][trackNumber]
            fileName = os.path.basename(filePath)
            fileNameWithoutExtension, extension = os.path.splitext(fileName)
            extension = extension.lower()

            if extension not in supportedExtensions:
                print(f"Couldn't tag : {fileName}, {extension} Not Supported Yet :(")
                tableData.append(('XX', 'XX', 'XX', fileName))
                continue

            trackData: TrackData = {
                **albumData,
                'track_number': trackNumber,
                'total_tracks': totalTracks,
                'disc_number': discNumber,
                'total_discs': totalDiscs,
                'file_path': filePath,
                'track_titles': trackTitles,
                'album_link': albumData.get('vgmdb_link'),
                'album_names': albumData.get('names'),
                'album_name': getBest(albumData.get('names'), flags.languageOrder)
            }
            # Tagging the file
            audioTagged = tagAudioFile(trackData, flags)

            if audioTagged:
                print(f"Tagged : {fileName}")
                tableData.append((
                    discNumber,
                    trackNumber,
                    getBest(trackTitles, flags.languageOrder),
                    fileName
                ))
            else:
                print(f"Couldn't tag : {fileName}")
                tableData.append(('XX', 'XX', 'XX', fileName))

    if not tableData:
        return
    print('\n', end='')

    print('Files Tagged as follows')
    tableData.sort()
    print(tabulate(tableData,
                   headers=['Disc', 'Track', 'Title', 'File Name'],
                   colalign=('center', 'center', 'left', 'left'),
                   maxcolwidths=53, tablefmt=tableFormat), end='\n\n')
