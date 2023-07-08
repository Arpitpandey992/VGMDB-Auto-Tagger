import argparse
from Imports.flagsAndSettings import Flags

from Modules.Rename.renameUtils import renameFilesRecursively
from Modules.Rename.renameUtils import organizeAlbum
from Utility.generalUtils import get_default_logger
from Utility.template import isValidTemplate


def argumentParser():
    parser = argparse.ArgumentParser(description='Organize a music album folder using file tags!')
    parser.add_argument('folderPath', type=str, help='Album directory path (Required Argument)')
    parser.add_argument('--rename-only', dest='rename_only', action='store_true',
                        help='Recursively Rename Files within Directory, considering no relationship between files')
    parser.add_argument('--same-folder-name', dest='same_folder_name', action='store_true',
                        help='use the current folder name instead of getting it from album name')
    parser.add_argument('--folder-naming-template',
                        dest='folder_naming_template',
                        type=str,
                        help='Give a folder naming template like {catalog}{foldername}{date}')
    parser.add_argument('--ksl', action='store_true',
                        help='for KSL folder, (custom setting), keep catalog first in naming')
    parser.add_argument('--wait', action='store_true',
                        help='pause after finishing script to review')
    args = parser.parse_args()
    return args


def main():
    args = argumentParser()
    logger = get_default_logger('Organize', 'info')
    folderPath = args.folderPath
    flags = Flags()
    folderNamingTemplate = flags.folderNamingTemplate

    if args.folder_naming_template:
        template = args.folder_naming_template
        if not isValidTemplate(template):
            logger.error("provided folder template is imbalanced, hence invalid, aborting!")
            exit(0)
        folderNamingTemplate = args.folder_naming_template

    if args.same_folder_name:
        folderNamingTemplate = "{[{date}] }{foldername}{ [{catalog}]}{ [{format}]}"
    if args.ksl:
        folderNamingTemplate = "{[{catalog}] }{albumname}{ [{date}]}{ [{format}]}"
    pauseOnFinish = args.wait
    logger.info(f"organizing {folderPath}")
    if args.rename_only:
        renameFilesRecursively(folderPath, verbose=True, pauseOnFinish=pauseOnFinish)
    else:
        organizeAlbum(folderPath, folderNamingtemplate=folderNamingTemplate, pauseOnFinish=pauseOnFinish)


if __name__ == '__main__':
    main()
