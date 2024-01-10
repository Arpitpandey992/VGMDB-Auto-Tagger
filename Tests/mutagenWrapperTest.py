import os
import string
import sys
import random
from typing import Callable, Optional
import unittest

sys.path.append(os.getcwd())
from Utility.Mutagen.mutagenWrapper import AudioFactory, pictureTypes, pictureNameToNumber

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
baseFolder = os.path.join(__location__, "testSamples")
coversPath = os.path.join(baseFolder, "covers")
covers = [os.path.join(coversPath, coverName) for coverName in os.listdir(coversPath)]

# Unicode range for common Japanese characters (Hiragana, Katakana, and common Kanji)
japanese_chars = [
    (0x3041, 0x3096),  # Hiragana
    (0x30A1, 0x30F6),  # Katakana
    (0x4E00, 0x9FBF),  # Common Kanji
]
all_japanese_chars = "".join(chr(x) for x in [k for start, end in japanese_chars for k in range(start, end)])


def getRandomCoverImageData() -> bytes:
    num_covers = len(covers)
    cover_index = random.randrange(0, num_covers, 1)
    path = covers[cover_index]
    # del covers[cover_index]
    with open(path, "rb") as image_file:
        image_data = image_file.read()
    return image_data


def generate_random_string(x: int, y: int):
    siz = random.randint(x, y)
    characters = string.ascii_letters + string.digits  # You can customize this further
    random_string = "".join(random.choice(characters) for _ in range(siz))
    return random_string


def generate_random_japanese_string(x: int, y: int) -> str:
    siz = random.randint(x, y)
    random_string = "".join(random.choice(all_japanese_chars) for _ in range(siz))
    return random_string


def selectRandomKeysFromDict(input_dict: dict) -> list:
    num_keys_to_select = random.randint(2, len(input_dict))
    dict_keys = list(input_dict.keys())
    selected_keys = random.sample(dict_keys, num_keys_to_select)
    return selected_keys


class MutagenWrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.audio = audioImpl
        self.file_path = filePathImpl

    def test_title(self):
        test_arr = ["title1", "title2", "title3", generate_random_string(5, 20), generate_random_japanese_string(8, 32)]
        self._test_equality_list_arg(self.audio.setTitle, self.audio.getTitle, test_arr)

    def test_album(self):
        test_arr = ["album1", "album2", generate_random_string(5, 20), "album4", generate_random_japanese_string(8, 32), generate_random_string(50, 200)]
        self._test_equality_list_arg(self.audio.setAlbum, self.audio.getAlbum, test_arr)

    def test_track_disc_number(self):
        disc, tot_discs, track, tot_tracks = 2, 5, 9, 55
        self.audio.setDiscNumbers(disc, tot_discs)
        self.audio.setTrackNumbers(track, tot_tracks)
        self.assertEqual(disc, self.audio.getDiscNumber())
        self.assertEqual(tot_discs, self.audio.getTotalDiscs())
        self.assertEqual(track, self.audio.getTrackNumber())
        self.assertEqual(tot_tracks, self.audio.getTotalTracks())

    def test_comment(self):
        test_arr = ["comment1", "find this album at vgmdb.net/damn_son", generate_random_string(5, 20), "album4", generate_random_japanese_string(8, 32), generate_random_string(50, 200)]
        self._test_equality_list_arg(self.audio.setComment, self.audio.getComment, test_arr)

    def test_date(self):
        test_arr = ["2001-7-3", "567-  4 /  14 ", "2023-9 -  4 ", "2023- 9", "1969 "]
        expected_arr = ["2001-07-03", "0567-04-14", "2023-09-04", "2023-09", "1969"]
        self._test_equality_list_arg(self.audio.setDate, self.audio.getDate, test_arr, expected_arr)

    def test_catalog(self):
        test_arr = ["KSLA-0211", "UNCD-0021~0025", generate_random_string(10, 10)]
        self._test_equality_list_arg(self.audio.setCatalog, self.audio.getCatalog, test_arr)

    def test_custom_tags(self):
        key = "MY_TAG"

        def generateValueList():
            return [generate_random_string(5, 35), "My_value", "testing  ...", "damn son ", generate_random_japanese_string(10, 20), generate_random_string(5, 15), "last custom tag"]

        self._test_equality_custom_tag(self.audio.setCustomTag, self.audio.getCustomTag, key, generateValueList())
        self._test_equality_list_arg(self.audio.setCatalog, self.audio.getCatalog, generateValueList())
        self._test_equality_list_arg(self.audio.setDiscName, self.audio.getDiscName, generateValueList())
        self._test_equality_list_arg(self.audio.setBarcode, self.audio.getBarcode, generateValueList())

    def test_getting_information(self):
        self.assertIsInstance(self.audio.printInfo(), str)

    def test_setting_deleting_front_cover(self):
        self.audio.setPictureOfType(getRandomCoverImageData(), "Cover (front)")
        self.assertTrue(self.audio.hasPictureOfType("Cover (front)"))

        self.audio.deletePictureOfType("Cover (front)")
        self.assertFalse(self.audio.hasPictureOfType("Cover (front)"))

    def test_setting_multiple_pictures(self):
        """This test is not for m4a files because they don't support multiple pictures"""
        chosen_picture_types = selectRandomKeysFromDict(pictureNameToNumber)  # random selection of which type of picture to embed
        # chosen_picture_types: list[pictureTypes] = [u'Other', u'File icon', u'Other file icon', u'Cover (front)', u'Cover (back)', u'Leaflet page', u'Media (e.g. lable side of CD)']
        for picture_type in chosen_picture_types:
            self.audio.setPictureOfType(getRandomCoverImageData(), picture_type)

        for picture_type in chosen_picture_types:
            self.assertTrue(self.audio.hasPictureOfType(picture_type))

    def test_xx_save(self):
        """xx is prepended so that the audio file is saved at the end"""
        self.audio.save()

    def _test_equality_list_arg(self, setter: Callable, getter: Callable, setter_arg: list, expected: Optional[list] = None):
        if not expected:
            expected = setter_arg

        setter([])
        self.assertEqual(None, getter())

        setter(setter_arg[0:1])
        self.assertEqual(expected[0:1], getter())

        setter(setter_arg)
        self.assertEqual(expected, getter())

    def _test_equality_custom_tag(self, setter: Callable, getter: Callable, key: str, val: list, expected: Optional[list] = None):
        if not expected:
            expected = val

        self.audio.setCustomTag(key, [])
        self.assertEqual(self.audio.getCustomTag(key), None)

        self.audio.setCustomTag(key, val[0:1])
        self.assertEqual(self.audio.getCustomTag(key), expected[0:1])

        self.audio.setCustomTag(key, val)
        self.assertEqual(self.audio.getCustomTag(key), expected)


extensions = ["mp3", "flac", "m4a", "wav", "ogg", "opus"]
for extension in extensions:
    suite = unittest.TestLoader().loadTestsFromTestCase(MutagenWrapperTestCase)
    print(f"\n----------------------------------------------------------------------\nTesting {extension} file")
    filePath = os.path.join(baseFolder, f"{extension}_test.{extension}")
    audioImpl = AudioFactory.buildAudioManager(filePath)
    audioImpl.clearTags()
    audioImpl.save()
    filePathImpl = filePath
    unittest.TextTestRunner().run(suite)
    # testMutagenWrapper(AudioFactory.buildAudioManager(filePath))
