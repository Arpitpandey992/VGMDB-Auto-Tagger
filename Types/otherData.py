from typing import Union, List, Optional
from typing_extensions import TypedDict, NotRequired, Required

from Imports.flagsAndSettings import Flags


class OtherData(TypedDict):
    folder_path: str
    flags: Flags
