from Imports.config import Config
from Modules.Scan.models.local_album_data import LocalAlbumData
from Modules.Utils.general_utils import getFirstOrNone
from Modules.organize.models.organize_result import FileOrganizeResult, FolderOrganizeResult


class Organizer:
    """Organizer class used to rename and move albums within the file system (preferrably after tagging)"""

    def __init__(self, local_album_data: LocalAlbumData, config: Config):
        self.local_album_data = local_album_data
        self.config = config
        self.sample_file = local_album_data.get_one_sample_track()
        self.audio_manager = self.sample_file.audio_manager
        self.album_template_mapping = self._get_album_template_mapping()

    def organize(self) -> FolderOrganizeResult:
        self.result = FolderOrganizeResult(old_path=self.local_album_data.album_folder_path)
        pass

    def commit_changes(self, folder_organize_result: FolderOrganizeResult):
        """manually commit changes given by organize function"""

    # Private Functions
    def _organize_album_files(self):
        for disc_number, disc in self.local_album_data.discs.items():
            total_tracks = disc.total_tracks
            isSingle = total_tracks == 1
            for track_number, file in disc.tracks.items():
                file_organize_result = FileOrganizeResult(old_path=file.file_path, base_album_path=self.local_album_data.album_folder_path)
                title = getFirstOrNone(file.audio_manager.getTitle())
                if not title:
                    logger.debug(f"title not present in file: {file.file_name}, using existing file name")

                trackNumberStr = getProperCount(track_number, total_tracks)
                discNumberStr = getProperCount(disc_number, totalDiscs)

                oldName = fullFileName

                if isSingle:
                    newName = f"{cleanName(f'{title}')}{extension}"
                else:
                    newName = f"{cleanName(f'{trackNumberStr} - {title}')}{extension}"
                discName = file.audio_manager.getDiscName()

                if discName:
                    discFolderName = f"Disc {disc_number} - {discName}"
                else:
                    discFolderName = f"Disc {disc_number}"

                if totalDiscs == 1 or noMove:
                    discFolderName = ""
                discFolderPath = os.path.join(folderPath, discFolderName)
                if not os.path.exists(discFolderPath):
                    os.makedirs(discFolderPath)
                newFilePath = os.path.join(discFolderPath, newName)
                if file != newFilePath:
                    try:
                        if os.path.exists(newFilePath):
                            logger.error(f"{newFilePath} exists, cannot rename {fileName}")
                        else:
                            os.rename(file, newFilePath)
                            printAndMoveBack(f"renamed: {newName}")
                            tableData.append((discNumberStr, trackNumberStr, oldName, os.path.join(discFolderName, newName)))

                    except Exception as e:
                        logger.exception(f"cannot rename {fileName}\n{e}")
        printAndMoveBack("")
        if verbose and tableData:
            logger.info("files renamed as follows:")
            tableData.sort()
            logger.info("\n" + tabulate(tableData, headers=["Disc", "Track", "Old Name", "New Name"], colalign=("center", "center", "left", "left"), maxcolwidths=50, tablefmt=Config().table_format))

    def _get_album_template_mapping(self) -> dict[str, str | None]:
        return {
            "albumname": getFirstOrNone(self.audio_manager.getAlbum()),
            "foldername": self.local_album_data.album_folder_name,
            "catalog": getFirstOrNone(self.audio_manager.getCatalog()),
            "date": self.audio_manager.getDate(),
            "barcode": getFirstOrNone(self.audio_manager.getCustomTag("barcode")),
            "format": self.sample_file.get_audio_source(),
        }
