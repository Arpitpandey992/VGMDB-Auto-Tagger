from typing import Optional
from pydantic import BaseModel

from Modules.Mutagen.mutagenWrapper import IAudioManager
from Modules.Print.utils import LINE_SEPARATOR, SUB_LINE_SEPARATOR


class Track(BaseModel):
    file_path: str
    depth_in_parent_folder: int
    audio_manager: IAudioManager

    class Config:
        arbitrary_types_allowed = True


class Disc(BaseModel):
    tracks: dict[int, Track] = {}
    folder_name: Optional[str] = None  # It may represent Disc Name for properly stored albums (like Disc 1: The Rime of the Ancient Mariner)


class LocalAlbumData(BaseModel):
    """
    an object containing the data of files representing an audio album present in a file system
    """

    album_folder_path: str
    discs: dict[int, Disc] = {}  # files with proper disc number (default = 1) and track numbers already present
    unclean_tracks: list[Track] = []  # files without track number tags, maybe we can still tag them somehow? (accoust_id, name similarity, etc)

    def pprint(self) -> str:
        """pretty printing only the useful information"""
        details = f"{LINE_SEPARATOR}\nalbum path: {self.album_folder_path}\n{LINE_SEPARATOR}\n"
        for disc_number, disc in sorted(self.discs.items()):
            details += f"Disc {disc_number}:{f' {disc.folder_name}' if disc.folder_name else ''}\n{SUB_LINE_SEPARATOR}\n"
            for track_number, track in sorted(disc.tracks.items()):
                details += f"Track {track_number}: {track.file_path}\n"
            details += f"{SUB_LINE_SEPARATOR}\n"
        details += f"{LINE_SEPARATOR}\n"
        return details

    # helper functions
    def does_track_exist(self, disc_number: int, track_number: int) -> bool:
        if disc_number not in self.discs or track_number not in self.discs[disc_number].tracks:
            return False
        return True

    def get_track(self, disc_number: int, track_number: int) -> Track:
        """Raises exception if track does not exist, use this function in conjunction with does_track_exist"""
        try:
            return self.discs[disc_number].tracks[track_number]
        except KeyError:
            raise KeyError(f"no track exists having disc number: {disc_number} and track number: {track_number}")

    def set_track(self, disc_number: int, track_number: int, track: Track):
        """writes over existing track if it exists"""
        if disc_number not in self.discs:
            self.discs[disc_number] = Disc()
        self.discs[disc_number].tracks[track_number] = track
