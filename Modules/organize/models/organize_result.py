import os
from pydantic import BaseModel

from Modules.organize.organize_utils import get_base_folder_under_parent


class FileOrganizeResult(BaseModel):
    old_path: str
    new_path: str | None = None
    base_album_path: str

    @property
    def old_name(self) -> str:
        """get name of file (without extension)"""
        return self._get_name_from_path(self.old_path)

    @property
    def new_name(self) -> str | None:
        """get name of modified file (without extension)"""
        return self._get_name_from_path(self.new_path) if self.new_path else None

    @property
    def extension(self) -> str:
        """get extension of file (like .flac, .mp3, etc)"""
        _, extension = os.path.splitext(self.old_path)
        return extension

    @property
    def old_disc_folder_name(self) -> str | None:
        """like album_name/disc_01/track1.mp3 -> disc_01"""
        return self._get_base_path_under_parent(self.old_path)

    @property
    def new_disc_folder_name(self) -> str | None:
        """like album_name/Disc 01. Old Tracks/Left Side/track1.mp3 -> Disc 01. Old Tracks/Left Side"""
        return self._get_base_path_under_parent(self.new_path) if self.new_path else None

    def _get_name_from_path(self, path: str) -> str:
        return self._get_name_without_extension(os.path.basename(path))

    def _get_name_without_extension(self, name: str) -> str:
        name_without_extension, _ = os.path.splitext(name)
        return name_without_extension

    def _get_base_path_under_parent(self, file_path: str) -> str | None:
        return get_base_folder_under_parent(file_path, self.base_album_path)


class FolderOrganizeResult(BaseModel):
    old_path: str
    new_path: str
    file_organize_results: list[FileOrganizeResult]

    @property
    def old_name(self) -> str:
        return os.path.basename(self.old_path)

    @property
    def new_name(self) -> str | None:
        return os.path.basename(self.new_path) if self.new_path else None
