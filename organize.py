import argparse
from Modules.OrganizeUtils.organizeAlbum import renameAndOrganizeFiles, renameFolder
from Modules.OrganizeUtils.renameFiles import renameFiles

parser = argparse.ArgumentParser(description='Organize a music album folder using file tags!')
parser.add_argument('folderPath', help='Album directory path (Required Argument)')
parser.add_argument('--rename-only', dest='rename_only', action='store_true',
                    help='Recursively Rename Files within Directory to {Track Number} - {Track Name}')
args = parser.parse_args()
folderPath = args.folderPath

if args.rename_only:
    renameFiles(folderPath)
else:
    renameAndOrganizeFiles(folderPath)
    renameFolder(folderPath)
