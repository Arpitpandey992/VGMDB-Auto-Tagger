import os
from typing import Optional
from Modules.Print.constants import SUB_LINE_SEPARATOR

from Modules.Scan import constants
from Modules.Tag import custom_tags
from Modules.Scan.models.local_album_data import LocalAlbumData, LocalTrackData
from Modules.Utils.general_utils import get_default_logger, is_date_in_YYYY_MM_DD, cleanDate
from unigen import AudioFactory, UnsupportedFileFormatError, isFileFormatSupported


"""
need to check if the folder contains exactly one album.
ways to identify:
    * Maximum depth must be less than constants.MAX_FOLDER_DEPTH_OF_ALBUM (=2) because folder structure can (or rather, should) be at max like:
        Album:
            Disc1:
                track1.flac
                track2.flac
            Disc2:
                track1.flac
            logs:
                extraction.log
            cue:
                album.cue
            thanks.txt
            cover.jpg
    * Only considering the depth of folders which contain at least one music file
    * For a folder to considered as an album, every audio file must have one of the following common amongst them entirely:
        * album name
        * catalog number
        * barcode
        * date (only if full date is available in YYYY-MM-DD form)
"""

logger = get_default_logger(__name__, "info")


class Scanner:
    def __init__(self, ensure_album_match: bool = True):
        self.ensure_album_match = ensure_album_match

    def scan_albums_recursively(self, root_dir: str) -> list[LocalAlbumData]:
        """scans for all albums inside root_folder recursively"""
        root_dir = self._convert_path_to_absolute(root_dir)
        max_depths: dict[str, int] = {}
        self._precalculate_max_depths_with_audio_files(root_dir, max_depths)
        albums = self._scan_albums_recursively(root_dir, max_depths)
        return albums

    def scan_album_in_folder_if_exists(self, folder_path: str) -> Optional[LocalAlbumData]:
        """returns a single album if the given folders contains files belonging to a single album"""
        folder_path = self._convert_path_to_absolute(folder_path)
        logger.info(SUB_LINE_SEPARATOR)
        logger.info(f"Scanning {folder_path}")
        logger.info(SUB_LINE_SEPARATOR)
        audio_files = self.get_supported_audio_files_in_folder(folder_path)
        if self.ensure_album_match and not self._does_audio_files_belong_to_one_album_only(audio_files):
            return None
        return self._compile_album_data_from_track_data(folder_path, audio_files)

    def get_supported_audio_files_in_folder(self, folder_path: str, max_depth: int = -1) -> list[LocalTrackData]:
        """get a list of all supported audio files inside a folder, provide max_depth for recursion depth while scanning"""
        folder_path = self._convert_path_to_absolute(folder_path)
        return self._get_supported_audio_files_in_folder(folder_path, max_depth)

    # private functions
    def _get_supported_audio_files_in_folder(self, folder_path: str, max_depth: int, current_depth: int = 1) -> list[LocalTrackData]:
        if max_depth > 0 and current_depth > max_depth:
            return []
        audio_tracks: list[LocalTrackData] = []
        for entry in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry)
            if os.path.isfile(entry_path):
                try:
                    audio_manager = AudioFactory.buildAudioManager(entry_path)
                    audio_tracks.append(LocalTrackData(file_path=entry_path, audio_manager=audio_manager, depth_in_parent_folder=current_depth))
                except UnsupportedFileFormatError:
                    pass
                except Exception as e:
                    logger.error(f"unable to read the file at {folder_path}, error:\n{e}")
            elif os.path.isdir(entry_path):
                audio_tracks.extend(self._get_supported_audio_files_in_folder(entry_path, max_depth, current_depth + 1))
        return audio_tracks

    def _compile_album_data_from_track_data(self, parent_directory: str, audio_files: list[LocalTrackData]) -> LocalAlbumData:
        """it is considered a guarantee that the audio_files array represents tracks of a single album"""
        album_data = LocalAlbumData(album_folder_path=parent_directory)

        # mapping tracks and discs
        for track_number_internal, track in enumerate(audio_files):
            if not self.ensure_album_match:
                # Since the tracks are individual files, we don't need to match anything
                album_data.set_track(1, track_number_internal + 1, track)  # disc number is not important here, just to avoid conflicts
                continue

            disc_number, track_number = track.audio_manager.getDiscNumber(), track.audio_manager.getTrackNumber()
            if not track_number:
                logger.info(f"track number not present in {track.file_name}, adding to unclean tracks")
                album_data.unclean_tracks.append(track)
                continue
            else:
                track_number = int(track_number)

            if not disc_number:
                logger.debug(f"disc number not present in {track.file_path}, taking default value: {constants.DEFAULT_DISC_NUMBER}")
                disc_number = constants.DEFAULT_DISC_NUMBER
            else:
                disc_number = int(disc_number)

            existing_track = album_data.get_track(disc_number, track_number)
            if existing_track:
                logger.error(f"{track.file_path} conflicts with {existing_track.file_path}, skipping this file")
                continue

            album_data.set_track(disc_number, track_number, track)

        # # setting the disc name if files are under a folder inside the album
        # def get_disc_folder_name(parent_directory: str, file_path: str) -> str | None:
        #     relative_path = os.path.relpath(os.path.normpath(file_path), os.path.normpath(parent_directory))
        #     base_dir = os.path.dirname(relative_path)
        #     return base_dir if base_dir not in ["", ".", "/"] else None

        # for disc_number, disc in album_data.discs.items():
        #     for track_number, track in disc.tracks.items():
        #         file_depth = track.depth_in_parent_folder
        #         if file_depth == 2:  # parent_folder -> Disc folder -> track.flac
        #             disc_name = get_disc_folder_name(parent_directory, track.file_path)
        #             if disc_name:
        #                 disc.disc_folder_name = disc_name
        #                 break

        return album_data

    def _does_audio_files_belong_to_one_album_only(self, audio_files: list[LocalTrackData]) -> bool:
        if not audio_files:
            return False

        def has_identical_items_list_of_list(arr: list[list[str]]) -> bool:
            common_items = set(arr[0])
            for item in arr:
                common_items.intersection_update(item)
                if len(common_items) == 0:
                    return False
            return True

        def has_identical_items_list_of_string(arr: list[str]) -> bool:
            return len(set(arr)) == len(arr)

        if has_identical_items_list_of_list([track.audio_manager.getCustomTag(custom_tags.VGMDB_LINK) for track in audio_files]):
            return True
        if has_identical_items_list_of_list([track.audio_manager.getAlbum() for track in audio_files]):
            return True
        if has_identical_items_list_of_list([track.audio_manager.getCatalog() for track in audio_files]):
            return True
        if has_identical_items_list_of_list([track.audio_manager.getBarcode() for track in audio_files]):
            return True
        dates = [track.audio_manager.getDate() for track in audio_files]
        if None not in dates:
            cleaned_dates = [date for date in dates if date is not None]
            if all(is_date_in_YYYY_MM_DD(cleanDate(date)) for date in cleaned_dates) and has_identical_items_list_of_string(cleaned_dates):
                return True
        return False

    def _scan_albums_recursively(self, folder_path: str, max_depths: dict[str, int]) -> list[LocalAlbumData]:
        max_depth = max_depths[folder_path]
        if max_depth != -1 and max_depth <= constants.MAX_FOLDER_DEPTH_OF_ALBUM:  # audio files exist somewhere inside the folder
            found_album = self.scan_album_in_folder_if_exists(folder_path)
            if found_album:
                return [found_album]

        found_albums: list[LocalAlbumData] = []
        for entry in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry)
            if os.path.isdir(entry_path):
                inner_albums = self._scan_albums_recursively(entry_path, max_depths)
                found_albums.extend(inner_albums)
        return found_albums

    def _precalculate_max_depths_with_audio_files(self, folder_path: str, max_depths: dict[str, int]):
        """returns: whether the folder contains any audio file"""
        max_depth = -1
        for entry in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry)
            if os.path.isdir(entry_path):
                self._precalculate_max_depths_with_audio_files(entry_path, max_depths)
                if max_depths[entry_path] != -1:  # there is an audio file inside entry_path
                    max_depth = max(max_depth, 1 + max_depths[entry_path])
            elif os.path.isfile(entry_path) and isFileFormatSupported(entry_path):
                max_depth = max(max_depth, 1)

        max_depths[folder_path] = max_depth

    def _convert_path_to_absolute(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.abspath(path)


if __name__ == "__main__":
    test_music_dir = "/Users/arpit/Library/Custom/Music"
    scanner = Scanner()
    albums = scanner.scan_albums_recursively(test_music_dir)
    for album in albums:
        print(album.pprint())
