import unittest
from Modules.Organize.organize_utils import extract_disc_name_from_folder_name, extract_disc_number_from_folder_name, extract_track_name_from_file_name, extract_track_number_from_file_name


class TestOrganizeUtils(unittest.TestCase):
    def setUp(self):
        self.disc_folder_names_tests = [
            ["disc01- what da dog doin?", "what da dog doin?", 1],
            ["cd 4 : damn", "damn", 4],
            ["6.    disc name   .", "disc name   .", 6],
            [" 8 ", None, 8],
            ["  Disc 003.  ", None, 3],
            ["  DIsc 003.  disc 005 - damn boi", "disc 005 - damn boi", 3],
            ["CD - huh", None, None],
            ["CD 55- huh", "huh", 55],
            ["Diks 3        ꞉  disc name?", None, None],
            ["      Disc   3        :  disc name?", "disc name?", 3],
            ["DVD 33 >  disccc nameeee  ", "disccc nameeee", 33],
            ["cD 00004꞉->  disccc NaMaeee  ", "disccc NaMaeee", 4],
            ["", None, None],
            ["disc1discname", "discname", 1],
            ["disc10     ", None, 10],
        ]
        self.file_names_tests = [
            ["01. file1.flac", "file1", 1],
            ["   4    damn_boi.m4a", "damn_boi", 4],
            [" 21 : parting of the bois?  .wav", "parting of the bois?", 21],
            ["unnumbered track.ogg", "unnumbered track", None],
            ["7.flac", None, 7],
            [" .mp3", None, None],
            [" .mp3.flac", "mp3", None],
            [" 45farewell song.opus", "farewell song", 45],
        ]

    def test_extracting_disc_name_and_number(self):
        for disc_folder_name, disc_name_expected, disc_number_expected in self.disc_folder_names_tests:
            disc_name = extract_disc_name_from_folder_name(disc_folder_name)  # type: ignore
            disc_number = extract_disc_number_from_folder_name(disc_folder_name)  # type: ignore
            print(f'foldername: "{disc_folder_name}"\ndisc number: {disc_number}\ndisc name: "{disc_name}"\n')
            self.assertEqual(disc_name, disc_name_expected)
            self.assertEqual(disc_number, disc_number_expected)

    def test_extracting_track_name_and_number(self):
        for file_name, file_name_expected, file_number_expected in self.file_names_tests:
            track_name = extract_track_name_from_file_name(file_name)  # type: ignore
            track_number = extract_track_number_from_file_name(file_name)  # type: ignore
            print(f'filename: "{file_name}"\ntrack number: {track_number}\ntrack name: "{track_name}"\n')
            self.assertEqual(track_name, file_name_expected)
            self.assertEqual(track_number, file_number_expected)


if __name__ == "__main__":
    unittest.main()
