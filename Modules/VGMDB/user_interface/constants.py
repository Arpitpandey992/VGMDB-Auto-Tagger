from enum import Enum


class choices(Enum):
    yes = "Yes"
    no = "No"
    go_back = "Go Back to Search Results"
    edit_configs = "Edit Configs"

    @classmethod
    def from_value(cls, value: str):
        for member in cls:
            if member.value == value:
                return member
        raise KeyError(f"No enum member found for value {value}")


CONFIG_MAP_FOR_TAG = {
    "Tag": "tag",
    "Organize": "organize",
    "Tag Title (Enable/Disable tagging title field)": "title",
    "Keep Title (don't overwrite current title)": "keep_title",
    "Album Data Only": "album_data_only",
    "Translate (will enable Keep Title as well for safety)": "translate",
}

REVERSE_CONFIG_MAP_FOR_TAG = {val: key for key, val in CONFIG_MAP_FOR_TAG.items()}

CONFIG_MAP_FOR_ORGANIZE = {
    "Rename Folder": "rename_folder",
    "Rename Files": "rename_files",
    "Same Folder Name (Use current folder name and add other fields on top like date)": "same_folder_name",
}

REVERSE_CONFIG_MAP_FOR_ORGANIZE = {val: key for key, val in CONFIG_MAP_FOR_ORGANIZE.items()}

NULL_INT = 10001
