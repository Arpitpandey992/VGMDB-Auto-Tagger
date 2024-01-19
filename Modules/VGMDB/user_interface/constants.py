from enum import Enum


class choices(Enum):
    yes = "Yes"
    no = "No"
    go_back = "Go Back to Search Results"
    edit_configs = "Edit Configs"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise KeyError(f"No enum member found for value {value}")


CONFIG_MAP = {
    "Tag": "tag",
    "Rename": "rename",
    "Tag Title (Enable/Disable tagging title field)": "title",
    "Keep Title (don't overwrite current title)": "keep_title",
    "Album Data Only": "album_data_only",
    "Translate": "translate",
}

REVERSE_CONFIG_MAP = {val: key for key, val in CONFIG_MAP.items()}
NULL_INT = 10001
