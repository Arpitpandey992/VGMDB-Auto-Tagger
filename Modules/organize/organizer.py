import os
from Imports.config import Config
from Modules.Mutagen.utils import getProperCount
from Modules.Scan.models.local_album_data import LocalAlbumData, LocalTrackData
from Modules.Utils.general_utils import get_default_logger, getFirstProperOrNone
from Modules.organize.models.organize_result import FileOrganizeResult, FolderOrganizeResult
from Modules.organize.template import TemplateResolver
from Modules.organize.organize_utils import clean_name, extract_disc_name_from_folder_name, extract_disc_number_from_folder_name, extract_track_name_from_file_name, extract_track_number_from_file_name, get_base_folder_under_parent

logger = get_default_logger(__name__, "info")


class Organizer:
    """Organizer class used to rename and move album within the file system (preferrably after tagging)"""

    def __init__(self, local_album_data: LocalAlbumData, config: Config):
        self.local_album_data = local_album_data
        self.config = config
        self.sample_file = local_album_data.get_one_sample_track()
        self.audio_manager = self.sample_file.audio_manager
        self.album_folder_path = local_album_data.album_folder_path

    def organize(self) -> FolderOrganizeResult:
        old_path = self.local_album_data.album_folder_path
        base_path = os.path.dirname(old_path)
        folder_naming_template_mapping = self._get_album_template_mapping()
        new_name = TemplateResolver(folder_naming_template_mapping).evaluate(self.config.folder_naming_template)
        new_path = os.path.join(base_path, new_name)
        files_organize_result = self._organize_album_files()

        return FolderOrganizeResult(old_path=old_path, new_path=new_path, file_organize_results=files_organize_result)

    def commit_changes(self, folder_organize_result: FolderOrganizeResult):
        """manually commit changes given by organize function"""
        if self.config.rename_files:
            for file_organize_result in folder_organize_result.file_organize_results:
                new_path = file_organize_result.new_path
                if not new_path:
                    logger.error(f"new name not present for {file_organize_result.old_name}")
                    continue
                if file_organize_result.old_path == new_path:
                    continue
                logger.info(f"renaming {file_organize_result.old_name} to {file_organize_result.new_name}")
                try:
                    base_folder_path = os.path.dirname(new_path)
                    os.makedirs(base_folder_path, exist_ok=True)
                    os.rename(file_organize_result.old_path, new_path)
                except Exception as e:
                    logger.error(f"error in renaming file {file_organize_result.old_name}: {e}")

        if self.config.rename_folder and folder_organize_result.new_path != folder_organize_result.old_path:
            if not folder_organize_result.new_path:
                logger.error(f"new name not present for {folder_organize_result.old_name}")
                return
            logger.info(f"renaming {folder_organize_result.old_name} to {folder_organize_result.new_name}")
            try:
                os.rename(folder_organize_result.old_path, folder_organize_result.new_path)
            except Exception as e:
                logger.error(f"error in renaming folder {folder_organize_result.old_name}: {e}")

    # Private Functions
    def _organize_album_files(self) -> list[FileOrganizeResult]:
        file_organize_results: list[FileOrganizeResult] = []

        total_discs = self.local_album_data.total_discs

        for disc_number, disc in self.local_album_data.discs.items():
            total_tracks = disc.total_tracks

            for track_number, file in disc.tracks.items():
                new_file_name = self._get_new_file_name(file, track_number=track_number, total_tracks=total_tracks, disc_number=disc_number, total_discs=total_discs)
                new_file_path = os.path.join(self.album_folder_path, new_file_name)
                file_organize_result = FileOrganizeResult(old_path=file.file_path, new_path=new_file_path, base_album_path=self.local_album_data.album_folder_path)
                file_organize_results.append(file_organize_result)

        for sort_number, file in enumerate(self.local_album_data.unclean_tracks):
            new_file_name = self._get_new_file_name(file, sort_number=sort_number)
            new_file_path = os.path.join(self.album_folder_path, new_file_name)
            file_organize_result = FileOrganizeResult(old_path=file.file_path, new_path=new_file_path, base_album_path=self.local_album_data.album_folder_path)
            file_organize_results.append(file_organize_result)

        return file_organize_results

    def _get_new_file_name(
        self,
        file: LocalTrackData,
        *,
        track_number: int | None = None,
        total_tracks: int | None = None,
        disc_number: int | None = None,
        total_discs: int | None = None,
        sort_number: int | None = None,
    ) -> str:
        """get new file path after renaming and moving file under disc if applicable (does not include base path, needs to be prepended later)"""

        is_album_single_disc = total_discs == 1
        is_disc_single = total_tracks == 1
        title = getFirstProperOrNone(file.audio_manager.getTitle())
        disc_folder_name = get_base_folder_under_parent(file.file_path, self.album_folder_path)

        track_number = track_number if track_number else self._get_track_number(file)
        total_tracks = total_tracks if total_tracks else self._get_total_tracks(file)
        disc_number = disc_number if disc_number else self._get_disc_number(file, disc_folder_name)
        total_discs = total_discs if total_discs else self._get_total_discs(file)
        disc_name = self._get_disc_name(file, disc_folder_name)
        file_name = extract_track_name_from_file_name(file.file_name)

        track_number_fixed, _ = getProperCount(track_number, total_tracks)
        disc_number_fixed, _ = getProperCount(disc_number, total_discs)
        fixed_sort_number, _ = getProperCount(sort_number + 1, len(self.local_album_data.unclean_tracks)) if sort_number else (None, None)

        disc_naming_template = self.config.disc_folder_naming_template_single if is_album_single_disc else self.config.disc_folder_naming_template_multiple
        disc_naming_template_mapping: dict[str, str | None] = {
            "discnumber": disc_number_fixed,
            "discname": disc_name,
            "discfoldername": disc_folder_name,
        }

        file_naming_template = self.config.file_naming_template_single if is_disc_single else self.config.file_naming_template_multiple
        file_naming_template_mapping: dict[str, str | None] = {
            "tracknumber": track_number_fixed,
            "sortnumber": fixed_sort_number,
            "tracktitle": title,
            "filename": file_name,
            "extension": file.extension,
        }

        new_disc_folder_name = clean_name(TemplateResolver(disc_naming_template_mapping).evaluate(disc_naming_template))
        new_file_name = clean_name(TemplateResolver(file_naming_template_mapping).evaluate(file_naming_template))

        return os.path.join(new_disc_folder_name, new_file_name)

    def _get_track_number(self, file: LocalTrackData) -> int | None:
        track_numbers: list[int | None] = [file.audio_manager.getTrackNumber(), extract_track_number_from_file_name(file.file_name)]
        return getFirstProperOrNone(track_numbers)

    def _get_total_tracks(self, file: LocalTrackData) -> int | None:
        return file.audio_manager.getTotalTracks()

    def _get_disc_number(self, file: LocalTrackData, disc_folder_name: str | None) -> int | None:
        disc_numbers: list[int | None] = [file.audio_manager.getDiscNumber(), extract_disc_number_from_folder_name(disc_folder_name)]
        return getFirstProperOrNone(disc_numbers)

    def _get_total_discs(self, file: LocalTrackData) -> int | None:
        return file.audio_manager.getTotalDiscs()

    def _get_disc_name(self, file: LocalTrackData, disc_folder_name: str | None) -> str | None:
        disc_names = [getFirstProperOrNone(file.audio_manager.getDiscName()), extract_disc_name_from_folder_name(disc_folder_name)]
        return getFirstProperOrNone(disc_names)

    def _get_album_template_mapping(self) -> dict[str, str | None]:
        return {
            "albumname": getFirstProperOrNone(self.audio_manager.getAlbum()) if not self.config.same_folder_name else None,
            "foldername": self.local_album_data.album_folder_name,
            "catalog": getFirstProperOrNone(self.audio_manager.getCatalog()),
            "date": self.audio_manager.getDate(),
            "barcode": getFirstProperOrNone(self.audio_manager.getCustomTag("barcode")),
            "format": self.sample_file.get_audio_source(),
        }
