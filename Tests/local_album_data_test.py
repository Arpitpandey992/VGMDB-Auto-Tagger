from typing import Literal
import unittest
from unittest.mock import MagicMock
from unigen import MediaInfo, AudioFactory
from unigen.wrapper.vorbis import VorbisWrapper

# REMOVE
import os
import sys

sys.path.append(os.getcwd())
# REMOVE

from Modules.Scan.models.local_album_data import LocalTrackData
from Tests.test_utils import get_test_file_path


class MockAudioManager(VorbisWrapper):
    def __init__(self, file_path: str, extension: Literal[".flac"] | Literal[".ogg"] | Literal[".opus"], mediaInfo: MediaInfo):
        super().__init__(file_path, extension)
        self.media_info = mediaInfo

    def getMediaInfo(self) -> MediaInfo:
        return self.media_info


class TestRenameTemplate(unittest.TestCase):
    def setUp(self):
        self.mock_audio = MagicMock()

    def test_get_audio_source_lossless(self):
        flac_file_path = get_test_file_path("flac")
        for extension in [".flac", ".wav"]:
            file_path = get_test_file_path(extension[1:])
            codec = extension[1:].upper()

            audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=45, channels=2, bits_per_sample=16, sample_rate=44100, codec=None))
            self.assertEqual(
                LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
                f"CD-{codec} 16bit 44kHz",
            )

            audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=45, channels=2, bits_per_sample=24, sample_rate=96000, codec=None))
            self.assertEqual(
                LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
                f"WEB-{codec} 24bit 96kHz",
            )

            audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=45, channels=2, bits_per_sample=32, sample_rate=96000, codec=None))
            self.assertEqual(
                LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
                f"VINYL-{codec} 32bit 96kHz",
            )

            audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=45, channels=2, bits_per_sample=24, sample_rate=210343, codec=None))
            self.assertEqual(
                LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
                f"VINYL-{codec} 24bit 210kHz",
            )

            audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=45, channels=2, bits_per_sample=None, sample_rate=None, codec=None))
            self.assertEqual(
                LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
                f"{codec}",
            )

            audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=45, channels=2, bits_per_sample=None, sample_rate=43552, codec=None))
            self.assertEqual(
                LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
                f"{codec} 43kHz",
            )

    def test_get_audio_source_mp3(self):
        flac_file_path = get_test_file_path("flac")
        extension = ".mp3"
        file_path = get_test_file_path(extension[1:])
        codec = "MP3"

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=320000, channels=2, bits_per_sample=16, sample_rate=44100, codec=None))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"CD-{codec} 320kbps",
        )

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=None, channels=2, bits_per_sample=16, sample_rate=44100, codec=None))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"CD-{codec}",
        )

    def test_get_audio_source_m4a(self):
        flac_file_path = get_test_file_path("flac")
        extension = ".m4a"
        file_path = get_test_file_path(extension[1:])

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=320000, channels=2, bits_per_sample=24, sample_rate=96000, codec="ALAC"))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"WEB-ALAC 24bit 96kHz",
        )

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=320000, channels=2, bits_per_sample=16, sample_rate=44100, codec="ALAC"))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"WEB-ALAC 16bit 44kHz",
        )

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=320000, channels=2, bits_per_sample=16, sample_rate=None, codec="ALAC"))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"WEB-ALAC 16bit",
        )

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=None, channels=2, bits_per_sample=16, sample_rate=44100, codec="AAC"))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"WEB-AAC",
        )

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=256056, channels=2, bits_per_sample=16, sample_rate=44100, codec="AAC"))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"WEB-AAC 256kbps",
        )

    def test_get_audio_source_ogg(self):
        flac_file_path = get_test_file_path("flac")
        extension = ".ogg"
        file_path = get_test_file_path(extension[1:])
        codec = "OGG"

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=320000, channels=2, bits_per_sample=16, sample_rate=44100, codec=None))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"WEB-{codec} 320kbps",
        )

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=None, channels=2, bits_per_sample=16, sample_rate=44100, codec=None))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"WEB-{codec}",
        )

    def test_get_audio_source_opus(self):
        flac_file_path = get_test_file_path("flac")
        extension = ".opus"
        file_path = get_test_file_path(extension[1:])
        codec = "OPUS"

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=320000, channels=2, bits_per_sample=16, sample_rate=44100, codec=None))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"YT-{codec}",
        )

        audio_manager = MockAudioManager(flac_file_path, ".flac", MediaInfo(bitrate=None, channels=2, bits_per_sample=16, sample_rate=44100, codec=None))
        self.assertEqual(
            LocalTrackData(file_path=file_path, depth_in_parent_folder=0, audio_manager=audio_manager).get_audio_source(),
            f"YT-{codec}",
        )


if __name__ == "__main__":
    unittest.main()
