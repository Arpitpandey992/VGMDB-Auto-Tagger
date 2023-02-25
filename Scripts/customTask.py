import os
from mutagen.flac import FLAC

# Define the input and output directories
input_dir = "/run/media/arpit/DATA/Music/Visual Novels/Key Sounds Label/Extra/HEAVEN BURNS RED (1)/New Folder"
output_dir = "/run/media/arpit/DATA/Music/Visual Novels/Key Sounds Label/Extra/HEAVEN BURNS RED (1)/New Folder/art"

# Loop over all files in the input directory
for file_name in os.listdir(input_dir):
    # Check if the file is a FLAC file
    if file_name.endswith(".flac"):
        # Load the FLAC file and get the album art
        file_path = os.path.join(input_dir, file_name)
        flac_file = FLAC(file_path)
        artwork = flac_file.pictures[0].data if flac_file.pictures else None
        # Save the album art to a file with the same name as the FLAC file
        if artwork:
            output_path = os.path.join(output_dir, file_name.replace(".flac", ".jpg"))
            with open(output_path, "wb") as f:
                f.write(artwork)
