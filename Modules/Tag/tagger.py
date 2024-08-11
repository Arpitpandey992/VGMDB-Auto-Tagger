from typing import Any

from Imports.config import Config
from Modules.Tag import custom_tags
from Modules.Scan.models.local_album_data import LocalAlbumData
from Modules.VGMDB.models.vgmdb_album_data import ArrangerOrComposerOrLyricistOrPerformer, Names, VgmdbAlbumData
from Modules.Utils.general_utils import get_default_logger, printAndMoveBack

logger = get_default_logger(__name__, "info")


class Tagger:
    """Tagger class, the audio files in vgmdb object must be linked to their local counterparts before this class is called"""

    def __init__(self, local_album_data: LocalAlbumData, vgmdb_album_data: VgmdbAlbumData, config: Config):
        self.local_album_data, self.vgmdb_album_data = local_album_data, vgmdb_album_data
        self.config = config
        self.matched_local_tracks = [track.local_track for _, disc in self.vgmdb_album_data.discs.items() for _, track in disc.tracks.items() if track.local_track]
        self.unmatched_local_tracks = self.vgmdb_album_data.unmatched_local_tracks

    def tag_files(self):
        if not self.config.album_data_only:
            logger.info("tagging track data")
            self._tag_track_specific_data()
            printAndMoveBack("")
            logger.info("finished")

        logger.info("tagging album data")
        self._tag_album_specific_data()
        printAndMoveBack("")
        logger.info("finished")

        logger.info("saving files")
        self._save_local_files()
        printAndMoveBack("")
        logger.info("finished")

    # Private Functions
    def _save_local_files(self):
        for local_track in self.matched_local_tracks + self.unmatched_local_tracks:
            printAndMoveBack(local_track.file_name)
            local_track.audio_manager.save()

    def _tag_album_specific_data(self):
        for local_track in self.matched_local_tracks + self.unmatched_local_tracks:
            audio_manager = local_track.audio_manager
            printAndMoveBack(local_track.file_name)
            if self.config.album_name:
                album_names = self._get_flag_filtered_names(self.vgmdb_album_data.names)
                audio_manager.setAlbum(album_names) if album_names else None

            if self.config.vgmdb_link:
                audio_manager.setComment([f"Find the tracklist at {self.vgmdb_album_data.vgmdb_link}"])
                audio_manager.setCustomTag(custom_tags.VGMDB_LINK, [self.vgmdb_album_data.vgmdb_link])
                audio_manager.setCustomTag(custom_tags.VGMDB_ID, [self.vgmdb_album_data.album_id])

            if self.config.album_cover:
                cover_data = self.vgmdb_album_data.get_album_cover_data()
                if cover_data:
                    if self.config.album_cover_overwrite:
                        audio_manager.deletePictureOfType("Cover (front)")
                    if not audio_manager.hasPictureOfType("Cover (front)"):
                        audio_manager.setPictureOfType(cover_data, "Cover (front)")

            if self.config.date and self.vgmdb_album_data.release_date:
                audio_manager.setDate(self.vgmdb_album_data.release_date)

            if self.config.catalog and self.vgmdb_album_data.catalog:
                audio_manager.setCatalog([self.vgmdb_album_data.catalog])

            if self.config.barcode and self.vgmdb_album_data.barcode:
                audio_manager.setBarcode([self.vgmdb_album_data.barcode])

            if self.config.organizations and self.vgmdb_album_data.organizations:
                for org in self.vgmdb_album_data.organizations:
                    org_name = org.names.get_highest_priority_name(self.config.language_order)
                    audio_manager.setCustomTag(org.role, [org_name]) if org_name else None

            if self.config.media_format:
                audio_manager.setCustomTag("Media Format", [self.vgmdb_album_data.media_format])

            def addMultiValues(tag: list[ArrangerOrComposerOrLyricistOrPerformer] | None, tagInFile: str, flag: bool = True):
                if not tag or not flag:
                    return
                dude_names = self._remove_duplicates([name for name in [dude.names.get_highest_priority_name(self.config.language_order) for dude in tag] if name])
                audio_manager.setCustomTag(tagInFile, dude_names) if dude_names else None

            is_single = self.vgmdb_album_data.total_tracks_in_album == 1
            addMultiValues(self.vgmdb_album_data.lyricists, custom_tags.LYRICIST, is_single or self.config.lyricists)
            addMultiValues(self.vgmdb_album_data.performers, custom_tags.PERFORMER, is_single or self.config.performers)
            addMultiValues(self.vgmdb_album_data.arrangers, custom_tags.ARRANGER, is_single or self.config.arrangers)
            addMultiValues(self.vgmdb_album_data.composers, custom_tags.COMPOSER, is_single or self.config.composers)

    def _tag_track_specific_data(self):
        for disc_number, disc in self.vgmdb_album_data.discs.items():
            for track_number, track in disc.tracks.items():
                if not track.local_track:
                    continue
                printAndMoveBack(f"tagging {track.local_track.file_name}")
                audio_manager = track.local_track.audio_manager

                if self.config.title:
                    titles = self._get_flag_filtered_names(track.names)
                    if self.config.keep_title:
                        titles = [*audio_manager.getTitle(), *titles]
                    audio_manager.setTitle(titles) if titles else None

                if self.config.disc_numbers:
                    audio_manager.setDiscNumbers(disc_number, self.vgmdb_album_data.total_discs)

                if self.config.track_numbers:
                    audio_manager.setTrackNumbers(track_number, disc.total_tracks)

    def _get_flag_filtered_names(self, names: Names) -> list[str]:
        reordered_names = self._remove_duplicates(names.get_reordered_names(self.config.language_order))
        return reordered_names if self.config.all_lang else reordered_names[:1]

    def _remove_duplicates(self, arr: list[Any]) -> list[Any]:
        return [x for i, x in enumerate(arr) if x not in arr[:i]]


if __name__ == "__main__":
    from Modules.Scan.scanner import Scanner
    from Modules.VGMDB.api.client import VgmdbClient

    folder = ""
    scanner = Scanner()
    local_album_data = scanner.scan_album_in_folder_if_exists(folder)
    vgmdb_album_data = VgmdbClient().get_album_details("27623")
    if not local_album_data:
        print(f"nothing found in {folder}")
        exit(0)
    for track in local_album_data.get_all_tracks():
        track.audio_manager.clearTags()
        track.audio_manager.setAlbum(["rewrite"])
        track.audio_manager.save()

    tagger = Tagger(local_album_data, vgmdb_album_data, Config(root_dir=folder, all_lang=True, album_cover_overwrite=True))
    tagger.tag_files()
