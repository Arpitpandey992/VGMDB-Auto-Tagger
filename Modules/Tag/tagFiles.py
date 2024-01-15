# remove
from re import T
import sys
import os

sys.path.append(os.getcwd())
# remove

from tabulate import tabulate
from Imports.config import get_config
from Modules.Scan.models.local_album_data import LocalAlbumData
from Modules.VGMDB.models.vgmdb_album_data import ArrangerOrComposerOrLyricistOrPerformer, Names, VgmdbAlbumData
from Utility.generalUtils import get_default_logger, printAndMoveBack

logger = get_default_logger(__name__, "info")


class Tagger:
    def __init__(self, local_album_data: LocalAlbumData, vgmdb_album_data: VgmdbAlbumData):
        self.local_album_data, self.vgmdb_album_data = local_album_data, vgmdb_album_data
        self.config = get_config()
        self.vgmdb_album_data.link_local_album_data(self.local_album_data)
        self.matched_local_tracks = [track.local_track for _, disc in self.vgmdb_album_data.discs.items() for _, track in disc.tracks.items() if track.local_track]
        self.unmatched_local_tracks = self.vgmdb_album_data.unmatched_local_tracks
        self.table_data = []

    def tag_files(self):
        logger.info("tagging track data")
        self._tag_track_specific_data()
        logger.info("tagging album data")
        self._tag_album_specific_data()
        logger.info("saving files")
        self._save_local_files()

    def print_table(self):
        printAndMoveBack("")
        logger.info("files Tagged as follows:")
        self.table_data.sort()
        logger.info("\n" + tabulate(self.table_data, headers=["Disc", "Track", "Title", "File Name"], colalign=("center", "center", "left", "left"), maxcolwidths=50, tablefmt=self.config.tableFormat))

    # Private Functions
    def _save_local_files(self):
        for local_track in self.matched_local_tracks + self.unmatched_local_tracks:
            printAndMoveBack(local_track.file_name)
            local_track.audio_manager.save()

    def _tag_album_specific_data(self):
        for local_track in self.matched_local_tracks + self.unmatched_local_tracks:
            audio_manager = local_track.audio_manager
            printAndMoveBack(local_track.file_name)
            if self.config.ALBUM_NAME:
                album_names = self._get_flag_filtered_names(self.vgmdb_album_data.names)
                audio_manager.setAlbum(album_names) if album_names else None

            if self.config.VGMDB_LINK:
                audio_manager.setComment([f"Find the tracklist at {self.vgmdb_album_data.vgmdb_link}"])
                audio_manager.setCustomTag("VGMDB Link", [self.vgmdb_album_data.vgmdb_link])

            if self.config.ALBUM_COVER:
                cover_data = self.vgmdb_album_data.get_album_cover_data()
                if cover_data:
                    if self.config.ALBUM_COVER_OVERWRITE:
                        audio_manager.deletePictureOfType("Cover (front)")
                    if not audio_manager.hasPictureOfType("Cover (front)"):
                        audio_manager.setPictureOfType(cover_data, "Cover (front)")

            if self.config.DATE and self.vgmdb_album_data.release_date:
                audio_manager.setDate(self.vgmdb_album_data.release_date)

            if self.config.CATALOG and self.vgmdb_album_data.catalog:
                audio_manager.setCatalog([self.vgmdb_album_data.catalog])

            if self.config.BARCODE and self.vgmdb_album_data.barcode:
                audio_manager.setBarcode([self.vgmdb_album_data.barcode])

            if self.config.ORGANIZATIONS and self.vgmdb_album_data.organizations:
                for org in self.vgmdb_album_data.organizations:
                    org_name = self._get_highest_priority_name(org.names)
                    audio_manager.setCustomTag(org.role, [org_name]) if org_name else None

            def addMultiValues(tag: list[ArrangerOrComposerOrLyricistOrPerformer] | None, tagInFile: str, flag: bool = True):
                if not tag or not flag:
                    return
                dude_names = [name for name in [self._get_highest_priority_name(dude.names) for dude in tag] if name]
                audio_manager.setCustomTag(tagInFile, dude_names) if dude_names else None

            addMultiValues(self.vgmdb_album_data.lyricists, "lyricist", self.config.LYRICISTS)
            addMultiValues(self.vgmdb_album_data.performers, "performer", self.config.PERFORMERS)
            addMultiValues(self.vgmdb_album_data.arrangers, "arranger", self.config.ARRANGERS)
            addMultiValues(self.vgmdb_album_data.composers, "composer", self.config.COMPOSERS)

        for local_track in self.unmatched_local_tracks:
            self.table_data.append((404, 404, "XX", local_track.file_name))

    def _tag_track_specific_data(self):
        for disc_number, disc in self.vgmdb_album_data.discs.items():
            for track_number, track in disc.tracks.items():
                if not track.local_track:
                    self.table_data.append((disc_number, track_number, self._get_highest_priority_name(track.names), "XX"))
                    continue
                audio_manager = track.local_track.audio_manager

                if self.config.TITLE:
                    titles = self._get_flag_filtered_names(track.names)
                    if self.config.KEEP_TITLE:
                        titles.extend(audio_manager.getTitle())
                    audio_manager.setTitle(titles) if titles else None

                if self.config.DISC_NUMBERS:
                    audio_manager.setDiscNumbers(disc_number, self.vgmdb_album_data.total_discs)

                if self.config.TRACK_NUMBERS:
                    audio_manager.setTrackNumbers(track_number, disc.total_tracks)

                self.table_data.append((disc_number, track_number, self._get_highest_priority_name(track.names), track.local_track.file_name))

    def _get_flag_filtered_names(self, names: Names) -> list[str]:
        reordered_names = names.get_reordered_names(self.config.language_order)
        return reordered_names if self.config.ALL_LANG else reordered_names[:1]

    def _get_highest_priority_name(self, names: Names) -> str | None:
        reordered_names = names.get_reordered_names(self.config.language_order)
        return reordered_names[0] if reordered_names else None


def tag_album(local_album_data: LocalAlbumData, vgmdb_album_data: VgmdbAlbumData):
    tagger = Tagger(local_album_data, vgmdb_album_data)
    tagger.tag_files()
    tagger.print_table()


if __name__ == "__main__":
    import Modules.Scan.Scanner as Scanner
    import Modules.VGMDB.api.client as Client

    folder = "/Users/arpit/Library/Custom/Music/Rewrite OST Bak"
    local_album_data = Scanner.scan_album_in_folder_if_exists(folder)
    vgmdb_album_data = Client.getAlbumDetails("27623")
    if not local_album_data:
        print(f"nothing found in {folder}")
        exit(0)
    for track in local_album_data.get_all_tracks():
        track.audio_manager.clearTags()
        track.audio_manager.setAlbum(["rewrite"])
        track.audio_manager.save()

    config = get_config()
    config.ALL_LANG = True
    config.ALBUM_COVER_OVERWRITE = True
    tag_album(local_album_data, vgmdb_album_data)
