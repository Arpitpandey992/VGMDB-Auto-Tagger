import unittest
from Modules.organize.template import TemplateResolver


class TestRenameTemplate(unittest.TestCase):
    def setUp(self):
        self.mapping: dict[str, str | None] = {
            "catalog": "KSLA-0020",
            "folderName": "Key Sounds Label 0020: Air Original Soundtrack",
            "date": "2020-01-05",
            "year": "2023",
            "barcode": "033325551233",
            "name": "damnson",
            "trACknumber": "04",
            "sortnUmber": "006",
            "trackTitle": "whichTrackMightThisBeHuh?",
            "fileName": "originalFileNameDuh",
            "extension": ".flac",
            "damn": "son",
        }

    def test_folder_reaname(self):
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{[{catalog}] }{name}{ [{date}]}"),
            f"[{self.mapping['catalog']}] damnson [{self.mapping['date']}]",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{[{catalog}] }{foldername| name}{ [{date}]}"),
            f"[{self.mapping['catalog']}] {self.mapping['folderName']} [{self.mapping['date']}]",
        )
        self.mapping["catalog"] = None
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{[{catalog}] }{name}{ [{date}]}"),
            f"{self.mapping['name']} [{self.mapping['date']}]",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{[{catalog  }] }{foldername | name}{ [{date}]}"),
            f"{self.mapping['folderName']} [{self.mapping['date']}]",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{[{catalog}] } {foldername |   name  }{ [{date}]}"),
            f" {self.mapping['folderName']} [{self.mapping['date']}]",
        )
        self.mapping["folderName"] = ""
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{[{catalog}] } {foldername |   name  }{ [{date}]}"),
            f" {self.mapping['name']} [{self.mapping['date']}]",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{[{catalog}] }{foldername| name}{ [ {year}]}"),
            f"{self.mapping['name']} [ {self.mapping['year']}]",
        )

    def test_file_name_rename(self):
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{{tracknumber|sortnumber}. }{tracktITle|filename}{extension}"),
            f"{self.mapping['trACknumber']}. {self.mapping['trackTitle']}{self.mapping['extension']}",
        )
        self.mapping["tracknumber"] = ""
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{{tracknumber|sortnumber}. }{tracktITle|filename}{extension}"),
            f"{self.mapping['sortnUmber']}. {self.mapping['trackTitle']}{self.mapping['extension']}",
        )
        self.mapping["sortnUmber"] = None
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{{tracknumber|sortnumber}. }{tracktITle|filename}{extension}"),
            f"{self.mapping['trackTitle']}{self.mapping['extension']}",
        )
        self.mapping["sortnUmber"] = "9909"
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{{{tracknumber|sortnumber}. }{tracktITle}|filename}{extension}"),
            f"{self.mapping['sortnUmber']}. {self.mapping['trackTitle']}{self.mapping['extension']}",
        )
        self.mapping["trackTitle"] = None  # what if title is not present in file, the name should remain same
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{{{tracknumber|sortnumber}. {tracktITle}}|  filename}{extension}"),
            f"{self.mapping['fileName']}{self.mapping['extension']}",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{{{tracknumber|sortnumber}. {tracktITle}}|damn|filename}{extension}"),
            f"{self.mapping['damn']}{self.mapping['extension']}",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("tracktITle|filename"),
            f"{self.mapping['fileName']}",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("filename |   tracktITle | "),
            f"{self.mapping['fileName']}",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{tracktitle|filename|damn}{extension}"),
            f"{self.mapping['fileName']}{self.mapping['extension']}",
        )
        self.mapping["fileName"] = None
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("{tracktitle|filename|damn}{extension}"),
            f"{self.mapping['damn']}{self.mapping['extension']}",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("filename |   tracktITle |   "),
            "   ",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate("filename |   tracktITle |Default Title"),
            "Default Title",
        )
        self.assertEqual(
            TemplateResolver(self.mapping).evaluate(""),
            "",
        )


if __name__ == "__main__":
    unittest.main()
