import re
import os
import argparse

folderPath = "/run/media/arpit/DATA/Downloads/Torrents/Key Sounds Label/[KSLA-B]/[2001.08.10] Natukage ／ nostalgia [KSLA-0002] [CD-FLAC]"
parser = argparse.ArgumentParser(
    description='Custom task')

parser.add_argument('folderPath', nargs='?', help='Album directory path')
args = parser.parse_args()
if args.folderPath:
    folderPath = args.folderPath
while folderPath[-1] == '/':
    folderPath = folderPath[:-1]


def rename_folder(folder_path):
    # Extract the date, catalog, and quality from the original folder name
    folder_name = os.path.basename(folder_path)
    match = re.search(
        r'^\[(\d{4}.\d{2}.\d{2})\] (.*) \[(.*)\] \[(.*)\]$', folder_name)
    if not match:
        print(f'{folder_name} does not match the expected pattern')
        return

    date = match.group(1)
    folder_name = match.group(2)
    catalog = match.group(3)
    quality = match.group(4)

    # Construct the new folder name
    new_folder_name = f'[{catalog}] {folder_name} [{date}] [{quality}]'

    # Rename the folder
    new_folder_path = os.path.join(
        os.path.dirname(folder_path), new_folder_name)
    os.rename(folder_path, new_folder_path)
    print(f'renamed {os.path.basename(folder_path)} to {new_folder_name}')


# Test the function
rename_folder(folderPath)
