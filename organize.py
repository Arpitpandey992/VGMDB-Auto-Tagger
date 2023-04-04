import argparse

from Modules.Rename.renameUtils import renameFilesRecursively
from Modules.Rename.renameUtils import organizeAlbum

parser = argparse.ArgumentParser(description='Organize a music album folder using file tags!')
parser.add_argument('folderPath', help='Album directory path (Required Argument)')
parser.add_argument('--rename-only', dest='rename_only', action='store_true',
                    help='Recursively Rename Files within Directory, considering no relationship between files')
parser.add_argument('--same-folder-name', dest='same_folder_name', action='store_true',
                    help='use the current folder name instead of getting it from album name')
args = parser.parse_args()
folderPath = args.folderPath

if args.rename_only:
    renameFilesRecursively(folderPath, verbose=True)
else:
    organizeAlbum(folderPath, sameFolderName=args.same_folder_name)
