import os

# REMOVE
import sys

from Modules.Organize.template import TemplateResolver

sys.path.append(os.getcwd())
# REMOVE
from pydantic import BaseModel, ConfigDict, Field
from unigen import IAudioManager
from Modules.Print.constants import LINE_SEPARATOR, SUB_LINE_SEPARATOR


class LocalTrackData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    file_path: str = Field(frozen=True)
    depth_in_parent_folder: int
    audio_manager: IAudioManager

    @property
    def file_name(self) -> str:
        return os.path.basename(os.path.normpath(self.file_path))

    @property
    def extension(self) -> str:
        """get extension of file (like .flac, .mp3, etc)"""
        _, extension = os.path.splitext(self.file_path)
        return extension

    def __hash__(self) -> int:
        return self.file_path.__hash__()  # for being able to create a set

    def get_audio_source(self) -> str | None:

        audio_source_format_lossless = "{{{source}-{codec}}|source|codec}{ {bits}bit}{ {sample_rate}kHz}"
        audio_source_format_lossy = "{{{source}-{codec}}|source|codec}{ {bitrate}kbps}"
        source = None
        codec = None
        bits = None
        sample_rate = None
        bitrate = None

        extension = self.extension.lower().strip()
        info = self.audio_manager.getMediaInfo()
        if extension in [".flac", ".wav"]:
            codec = "FLAC" if extension == ".flac" else "WAV"
            bits = info.bits_per_sample

            if info.sample_rate:
                sample_rate = int(info.sample_rate / 1000)
            if bits:
                source = "CD" if bits == 16 else "WEB"
            if (sample_rate and sample_rate >= 192) or (bits and bits > 24):
                source = "VINYL"  # Scuffed way, but assuming Vinyl rips have extremely high sample rate, but Qobuz does provide 192kHz files so yeah...
            # Edge cases should be edited manually later

            return TemplateResolver(
                {
                    "source": source,
                    "codec": codec,
                    "bits": str(bits) if bits else None,
                    "sample_rate": str(sample_rate) if sample_rate else None,
                }
            ).evaluate(audio_source_format_lossless)

        elif extension == ".mp3":
            # CD-MP3 because in 99% cases, an mp3 album is a lossy cd rip
            source = "CD"
            codec = "MP3"
            bitrate = int(info.bitrate / 1000) if info.bitrate else None

        elif extension == ".m4a" or extension == ".aac":
            # aac files are usually provided by websites directly for lossy versions. apple music files are also m4a, m4a can also contain Apple ALAC files
            bitrate = int(info.bitrate / 1000) if info.bitrate else None
            if info.codec and info.codec.lower() == "alac":
                source = "WEB"
                codec = "ALAC"
                bits = info.bits_per_sample
                sample_rate = int(info.sample_rate / 1000) if info.sample_rate else None

                return TemplateResolver(
                    {
                        "source": source,
                        "codec": codec,
                        "bits": str(bits) if bits else None,
                        "sample_rate": str(sample_rate) if sample_rate else None,
                    }
                ).evaluate(audio_source_format_lossless)
            else:
                source = "WEB"
                codec = "AAC"

        elif extension == ".ogg":
            # Usually from spotify
            bitrate = int(info.bitrate / 1000) if info.bitrate else None
            source = "WEB"
            codec = "OGG"

        elif extension == ".opus":
            # YouTube bruh
            source = "YT"
            codec = "OPUS"
            bitrate = int(info.bitrate / 1000) if info.bitrate else None

        return TemplateResolver(
            {
                "source": source,
                "codec": codec,
                "bitrate": str(bitrate) if bitrate else None,
            }
        ).evaluate(audio_source_format_lossy)


class LocalDiscData(BaseModel):
    tracks: dict[int, LocalTrackData] = {}

    @property
    def total_tracks(self) -> int:
        return len(self.tracks)


class LocalAlbumData(BaseModel):
    """
    an object containing the data of files representing an audio album present in a file system
    """

    album_folder_path: str
    discs: dict[int, LocalDiscData] = {}  # files with proper disc number (default = 1) and track numbers already present
    unclean_tracks: list[LocalTrackData] = []  # files without track number tags, maybe we can still tag them somehow? (accoust_id, name similarity, etc)

    @property
    def album_folder_name(self) -> str:
        return os.path.basename(self.album_folder_path)

    @property
    def total_discs(self):
        return len(self.discs)

    @property
    def total_tracks_in_album(self):
        return sum(len(disc.tracks) for disc in self.discs.values()) + len(self.unclean_tracks)

    # helper functions
    def pprint(self) -> str:
        """pretty printing only the useful information"""
        details = f"{LINE_SEPARATOR}\nalbum path: {self.album_folder_path}\n{LINE_SEPARATOR}\n"
        for disc_number, disc in sorted(self.discs.items()):
            details += f"Disc {disc_number}\n{SUB_LINE_SEPARATOR}\n"
            for track_number, track in sorted(disc.tracks.items()):
                details += f"Track {track_number}: {track.file_path}\n"
            details += f"{SUB_LINE_SEPARATOR}\n"
        details += f"{LINE_SEPARATOR}\n"
        return details

    def get_track(self, disc_number: int, track_number: int) -> LocalTrackData | None:
        return self.discs[disc_number].tracks[track_number] if self._does_track_exist(disc_number, track_number) else None

    def set_track(self, disc_number: int, track_number: int, track: LocalTrackData):
        """writes over existing track if it exists"""
        if disc_number not in self.discs:
            self.discs[disc_number] = LocalDiscData()
        self.discs[disc_number].tracks[track_number] = track

    def get_all_tracks(self) -> list[LocalTrackData]:
        tracks = [track for track in self.unclean_tracks]
        tracks.extend([track for _, disc in self.discs.items() for _, track in disc.tracks.items()])
        return tracks

    def get_one_sample_track(self) -> LocalTrackData:
        all_tracks = self.get_all_tracks()
        return all_tracks[0] if all_tracks else self.unclean_tracks[0]  # if there are no clean tracks, there must be at least one unclean track

    def _does_track_exist(self, disc_number: int, track_number: int) -> bool:
        if disc_number not in self.discs or track_number not in self.discs[disc_number].tracks:
            return False
        return True


def test():
    from Modules.Scan.Scanner import Scanner

    test_music_dir = "/mnt/f/Music/Visual Novels/Key Sounds Label/KSLC/[KSLC-0006～7] Key Net Radio Vol.1 [2009.02.28] [Data-CD, CD-FLAC]"
    scanner = Scanner()
    album = scanner.scan_album_in_folder_if_exists(test_music_dir)
    if not album:
        return
    sample = album.get_one_sample_track()
    print(sample.get_audio_source())
    print(album.pprint())
    LocalAlbumData(**album.model_dump())


if __name__ == "__main__":
    test()
