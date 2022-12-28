import os
import mutagen
import math

# Set the directory containing the music files
directory = "/run/media/arpit/DATA/OSTs/Visual Novels/07th Expansion/01 - Higurashi/04 - Anime, Movies, TV/8. Higurashi Sotsu/[2021.11.26] [KAXA-8151CD] When They Cry-Sotsu Original Soundtrack CD - Kenji Kawai"

# Iterate through all the files in the directory
for filename in os.listdir(directory):
    # Load the file using mutagen
    if not filename.endswith('.flac') and not filename.endswith('.mp3'):
        continue

    audio_file = mutagen.File(os.path.join(directory, filename))
    # Skip the file if it is not an MP3 or FLAC file

    # Skip the file if the track number or title tags are not present or are empty
    if 'TRACKNUMBER' not in audio_file.tags or not audio_file.tags['TRACKNUMBER']:
        continue
    if 'TITLE' not in audio_file.tags or not audio_file.tags['TITLE']:
        continue

    # Get the track number and title from the tags
    track_number = audio_file.tags['TRACKNUMBER'][0]
    if isinstance(track_number, int):
        track_number = str(track_number)
    title = audio_file.tags['TITLE'][0]

    # Get the extension of the original file
    extension = os.path.splitext(filename)[1]

    # Construct the new filename
    new_filename = f'{int(track_number):02d}. {title}{extension}'
    print(f'Renamed {filename} to {new_filename}')
    # Rename the file
    os.rename(os.path.join(directory, filename),
              os.path.join(directory, new_filename))

print('Done!')
