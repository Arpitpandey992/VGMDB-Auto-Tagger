import argparse
from Modules.renameAndOrganize.renameAndOrganize import renameFiles, renameFolder


parser = argparse.ArgumentParser(description='Organize a music album folder using file tags!')
parser.add_argument('folderPath', help='Album directory path (Required Argument)')

args = parser.parse_args()
folderPath = args.folderPath

renameFiles(folderPath)
renameFolder(folderPath)
