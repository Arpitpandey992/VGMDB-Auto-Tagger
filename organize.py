import argparse

from Modules.Rename.renameUtils import renameFiles
from Modules.Rename.renameUtils import organizeAlbum

parser = argparse.ArgumentParser(description='Organize a music album folder using file tags!')
parser.add_argument('folderPath', help='Album directory path (Required Argument)')
parser.add_argument('--rename-only', dest='rename_only', action='store_true',
                    help='Recursively Rename Files within Directory')
parser.add_argument('--same-folder-name', dest='same_folder_name', action='store_true',
                    help='Keep the same folder name as [date] {foldername} [Catalog]')
args = parser.parse_args()
folderPath = args.folderPath

if args.rename_only:
    renameFiles(folderPath)
else:
    organizeAlbum(folderPath, sameFolderName=args.same_folder_name)
