import os
import sys

folder_path = sys.argv[1]

# Get the list of files in the folder
files = os.listdir(folder_path)

# Sort the files in ascending order
sorted_files = sorted(files)

if sorted_files:
    # Remove the first file
    first_file = sorted_files[0]
    file_path = os.path.join(folder_path, first_file)
    os.remove(file_path)
    print(f"Removed the file: {first_file}")
else:
    print("No files found in the folder.")
