from typing_extensions import TypedDict

from Imports.flagsAndSettings import Flags


class OtherData(TypedDict):
    folder_path: str
    flags: Flags
