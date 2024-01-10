from math import ceil, log10
from typing import Any, Literal, Optional, Union
from enum import Enum

from Utility.generalUtils import get_default_logger

logger = get_default_logger(__name__, 'info')


def isString(var) -> bool:
    return isinstance(var, str)


def splitAndGetFirst(discNumber: Optional[str]) -> Optional[str]:
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 4
    # output is a string, input can be an integer, float, ...
    if not discNumber:
        return None
    if not isString(discNumber):
        return str(discNumber)

    if '/' in discNumber:
        discNumber = discNumber.split('/')[0]
    elif ':' in discNumber:
        discNumber = discNumber.split(':')[0]

    return discNumber


def splitAndGetSecond(discNumber: Optional[str]) -> Optional[str]:
    # get the count of tracks -> checks if the input is something like 4/20 -> truncates to 20
    # output is a string, input can be an integer, float, ...
    if not discNumber:
        return None
    if not isString(discNumber):
        return str(discNumber)

    if '/' in discNumber:
        discNumberElements = discNumber.split('/')
        if len(discNumberElements) < 2:
            return None
        discNumber = discNumberElements[1]
    elif ':' in discNumber:
        discNumberElements = discNumber.split(':')
        if len(discNumberElements) < 2:
            return None
        discNumber = discNumberElements[1]
    else:
        return None
    return discNumber


def getFirstElement(listVariable: Optional[Union[list, Any]]) -> Any:
    if type(listVariable) is not list:
        return listVariable
    return listVariable[0]


pictureNameToNumber = {
    u'Other': 0,
    u'File icon': 1,
    u'Other file icon': 2,
    u'Cover (front)': 3,
    u'Cover (back)': 4,
    u'Leaflet page': 5,
    u'Media (e.g. lable side of CD)': 6,
    u'Lead artist/lead performer/soloist': 7,
    u'Artist/performer': 8,
    u'Conductor': 9,
    u'Band/Orchestra': 10,
    u'Composer': 11,
    u'Lyricist/text writer': 12,
    u'Recording Location': 13,
    u'During recording': 14,
    u'During performance': 15,
}

pictureTypes = Literal[
    u'Other',
    u'File icon',
    u'Other file icon',
    u'Cover (front)',
    u'Cover (back)',
    u'Leaflet page',
    u'Media (e.g. lable side of CD)',
    u'Lead artist/lead performer/soloist',
    u'Artist/performer',
    u'Conductor',
    u'Band/Orchestra',
    u'Composer',
    u'Lyricist/text writer',
    u'Recording Location',
    u'During recording',
    u'During performance'
]


def getProperCount(count: Union[str, int], totalCount: Union[str, int]) -> tuple[str, str]:
    """
    if total tracks = 100, then this function will convert 1 to 001 for consistent sorting
    getProperCount(4,124) will return ["004", "124"]
    """
    try:
        upperBound = int(ceil(log10(int(totalCount) + 1)))
        return str(count).zfill(upperBound), str(totalCount)
    except Exception as e:
        logger.exception(e)

    return str(count), str(totalCount)


def convertStringToNumber(var: Optional[str]) -> Optional[int]:
    if not var:
        return None
    return int(var)


def ensureOneOrNone(var: Optional[list]) -> Optional[list]:
    if (not var):  # Considers both cases: var is None or var is an empty array
        return None
    return var


def cleanDate(date_str: str) -> str:
    """
    Makes sure that date is in the form YYYY-MM-DD
    fills unknows fields with 00
    """
    ideal_parts_example = ["2014", "05", "13"]
    cleaned_date = date_str.strip().replace('/', '-').replace('_', '-').replace(' ', '')
    parts = cleaned_date.split('-')
    # parts += ['00'] * (len(ideal_parts_example) - len(parts)) # not appending 00 for now, this may not be the best way to do things
    parts = [_ensureNumCharacters(part, len(ideal_parts_example[i])) for i, part in enumerate(parts)]
    # normalized_date_str = '{}-{}-{}'.format(*parts)
    return "-".join(parts)


def extractYearFromDate(dat: Optional[str]) -> Optional[str]:
    if not dat:
        return None
    cleaned_date = cleanDate(dat)
    return cleaned_date[0:4] if len(cleaned_date) >= 4 else None


def checkForEmptyListArgument(func):
    def wrapper(self, *args, **kwargs):
        for arg in args:
            if not arg and isinstance(arg, list):
                logger.debug(f"received an empty list for function call: {func.__name__} under class: {self.__class__.__name__} in file: {self.audio.filename}")
                return  # Return early if the list is empty
        return func(self, *args, **kwargs)
    return wrapper


def _ensureNumCharacters(s: str, numCharacters: int) -> str:
    """prepends 0 to string to ensure there are numCharacters characters present in the string"""
    if len(s) >= numCharacters:
        return s
    return "0" * (numCharacters - len(s)) + s


if __name__ == "__main__":
    print(getProperCount(4, "124"))
    print(getProperCount("45", 1240))
    print(getProperCount(3, 28))

    print(cleanDate("567-  4 /  14 "))
    print(cleanDate("2023-9 -  4 "))
    print(cleanDate("2023- 9"))
