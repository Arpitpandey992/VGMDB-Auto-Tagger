import re
from math import ceil, log10
from sys import exception
from typing import Any, Literal, Optional, Union

from Modules.Utils.general_utils import get_default_logger

logger = get_default_logger(__name__, "info")

pictureTypes = Literal[
    "Other",
    "File icon",
    "Other file icon",
    "Cover (front)",
    "Cover (back)",
    "Leaflet page",
    "Media (e.g. lable side of CD)",
    "Lead artist/lead performer/soloist",
    "Artist/performer",
    "Conductor",
    "Band/Orchestra",
    "Composer",
    "Lyricist/text writer",
    "Recording Location",
    "During recording",
    "During performance",
]

pictureNameToNumber: dict[pictureTypes, int] = {
    "Other": 0,
    "File icon": 1,
    "Other file icon": 2,
    "Cover (front)": 3,
    "Cover (back)": 4,
    "Leaflet page": 5,
    "Media (e.g. lable side of CD)": 6,
    "Lead artist/lead performer/soloist": 7,
    "Artist/performer": 8,
    "Conductor": 9,
    "Band/Orchestra": 10,
    "Composer": 11,
    "Lyricist/text writer": 12,
    "Recording Location": 13,
    "During recording": 14,
    "During performance": 15,
}

pictureNumberToName: dict[int, pictureTypes] = {number: name for name, number in pictureNameToNumber.items()}


def isString(var: Any) -> bool:
    return isinstance(var, str)


def toString(var: Any) -> str:
    return str(var) if var is not None else var


def splitAndGetFirst(discNumber: Optional[str]) -> Optional[str]:
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 4
    # output is a string, input can be an integer, float, ...
    if not discNumber:
        return None
    if not isString(discNumber):
        return str(discNumber)

    if "/" in discNumber:
        discNumber = discNumber.split("/")[0]
    elif ":" in discNumber:
        discNumber = discNumber.split(":")[0]

    return discNumber


def splitAndGetSecond(discNumber: Optional[str]) -> Optional[str]:
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 20
    # output is a string, input can be an integer, float, ...
    if not discNumber:
        return None
    if not isString(discNumber):
        return str(discNumber)

    if "/" in discNumber:
        discNumberElements = discNumber.split("/")
        if len(discNumberElements) < 2:
            return None
        discNumber = discNumberElements[1]
    elif ":" in discNumber:
        discNumberElements = discNumber.split(":")
        if len(discNumberElements) < 2:
            return None
        discNumber = discNumberElements[1]
    else:
        return None
    return discNumber


def getFirstElement(listVariable: list[Any] | Any) -> Any:
    if isinstance(listVariable, list):
        return listVariable[0] if listVariable else None
    return listVariable


def getProperCount(count: str | int | None, totalCount: str | int | None) -> tuple[str, str]:
    """
    if total tracks = 100, then this function will convert 1 to 001 for consistent sorting
    getProperCount(4,124) will return ["004", "124"]
    will return count and total_count as strings (without modification) if either is not provided
    """
    if count and totalCount:
        try:
            upperBound = int(ceil(log10(int(totalCount) + 1)))
            return str(count).zfill(upperBound), str(totalCount)
        except Exception as e:
            logger.error(f"exception while standardizing count. returning as it is. Error: {e}")
    else:
        logger.error(f"both count and totalCount are required for standardizing counts, returning as it is. provided count: {count}, totalCount: {totalCount}")
    return toString(count), toString(totalCount)


def convertStringToNumber(var: Optional[str]) -> Optional[int]:
    if not var:
        return None
    return int(var)


def toList(var: Optional[list[Any]]) -> list[Any]:
    """converts None to empty list"""
    if not var:
        return []
    return var


def is_date_in_YYYY_MM_DD(date: str) -> bool:
    if not date:
        return False
    pattern = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$")
    return bool(pattern.match(date[0]))


def cleanDate(date_str: str) -> str:
    """
    Makes sure that date is in the form YYYY-MM-DD or YYYY-MM or YYYY
    """
    ideal_parts_example = ["2014", "05", "13"]
    cleaned_date = date_str.strip().replace("/", "-").replace("_", "-").replace(" ", "")
    parts = cleaned_date.split("-")
    # parts += ['00'] * (len(ideal_parts_example) - len(parts)) # not appending 00 for now, this may not be the best way to do things
    parts = [_ensureNumCharacters(part, len(ideal_parts_example[i])) for i, part in enumerate(parts)]
    # normalized_date_str = '{}-{}-{}'.format(*parts)
    return "-".join(parts)


def extractYearFromDate(date: Optional[str]) -> Optional[str]:
    if not date:
        return None
    cleaned_date = cleanDate(date)
    return cleaned_date[0:4] if len(cleaned_date) >= 4 else None


def _ensureNumCharacters(s: str, numCharacters: int) -> str:
    """prepends 0 to string to ensure there are numCharacters characters present in the string"""
    if len(s) >= numCharacters:
        return s
    return "0" * (numCharacters - len(s)) + s


if __name__ == "__main__":
    print(getProperCount(4, "124"))
    print(getProperCount("45", 1240))
    print(getProperCount(3, 28))
    print(getProperCount("12", 244))
    print(getProperCount("12", ""))
    print(getProperCount("1", None))
    print(getProperCount(4, 7))
    print(getProperCount("50", 2440))
    print(getProperCount(None, None))
    print(getProperCount(6, "60"))

    print(cleanDate("567-  4 /  14 "))
    print(cleanDate("2023-9 -  4 "))
    print(cleanDate("2023- 9"))
