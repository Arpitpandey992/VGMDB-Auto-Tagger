import hashlib
import os
import re
import sys
import logging
from typing import Any, Literal, Union, Optional
from math import ceil, log10
from dotenv import load_dotenv

load_dotenv()

logging_levels = Literal["info", "debug", "error", "critical", "fatal"]


def get_default_logger(name: str, logging_level: logging_levels = "info") -> logging.Logger:
    logging_levels = {"info": logging.INFO, "debug": logging.DEBUG, "error": logging.ERROR, "critical": logging.CRITICAL, "fatal": logging.FATAL}
    if logging_level not in logging_levels:
        raise Exception(f'invalid logging level: {logging_level}, choose among {", ".join(logging_levels.keys())}')
    level = logging_levels[logging_level]
    if logging_level == "info":
        logging.basicConfig(format="%(message)s")
    else:
        logging.basicConfig(format="%(levelname)s:\t  %(name)s: %(message)s")
    logger = logging.getLogger(name)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.abspath(os.path.join(script_dir, "..", "logs"))
    os.makedirs(logs_dir) if not os.path.exists(logs_dir) else None
    logger.addHandler(logging.FileHandler(os.path.join(logs_dir, f"{name}.log")))
    logger.setLevel(level)
    return logger


logger = get_default_logger(__name__, "info")


def isString(var: Any) -> bool:
    return isinstance(var, str)


def toString(var: Any) -> str:
    return str(var) if var is not None else var


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
            print(f"exception while standardizing count. returning as it is. Error: {e}")
    else:
        print(f"both count and totalCount are required for standardizing counts, returning as it is. provided count: {count}, totalCount: {totalCount}")
    return toString(count), toString(totalCount)


def ifNot(var: Any, otherwise: Any) -> Any:
    """checks if var is None (or empty list and all) and returns otherwise, else returns var"""
    return var if var else otherwise


def getFirstProperOrNone(var: list[Any] | None) -> Any | None:
    """return first proper (satisfies bool(element)) from list"""
    if not var:
        return None
    for item in var:
        if item:
            return item
    return None


def fixDate(date: Optional[str]) -> Optional[str]:
    """
    Makes sure that date is in the form YYYY-MM-DD
    fills unknows fields with 00
    """
    if not date:
        return date
    date.replace("/", "-")
    date.replace("_", "-")
    date = date.strip()
    parts = date.split("-")
    parts += ["00"] * (3 - len(parts))
    normalized_date_str = "{}-{}-{}".format(*parts)
    return normalized_date_str


def cleanSearchTerm(name: Optional[str]) -> Optional[str]:
    if name is None:
        return None

    def isJapanese(ch: str) -> bool:
        return ord(ch) >= 0x4E00 and ord(ch) <= 0x9FFF

    def isChinese(ch: str) -> bool:
        return ord(ch) >= 0x3400 and ord(ch) <= 0x4DFF

    ans = ""
    for ch in name:
        if ch.isalnum() or ch == " " or isJapanese(ch) or isChinese(ch):
            ans += ch
        else:
            ans += " "
    return ans


def printAndMoveBack(text: str):
    print(text, end="\r")
    sys.stdout.flush()
    sys.stdout.write("\033[K")  # Clear to the end of line, this will not clear the current line because we are not flushing stdout at this point


def getSha256(filePath: str, block_size: int = 8192) -> str:
    sha256Hash = hashlib.sha256()
    with open(filePath, "rb") as file:
        for block in iter(lambda: file.read(block_size), b""):
            sha256Hash.update(block)
    return sha256Hash.hexdigest()


def to_sentence_case(input_string: str) -> str:
    do_not_capitalize = ("a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "by", "of", "in", "is", "are")
    words = input_string.split()
    capitalized_words = [words[0].capitalize()] + [word if word.isupper() or word.lower() in do_not_capitalize else word.capitalize() for word in words[1:]]
    sentence_case_string = " ".join(capitalized_words)
    return sentence_case_string


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


def extractYearFromDate(date: str | None) -> str | None:
    if not date:
        return None
    cleaned_date = cleanDate(date)
    return cleaned_date[0:4] if len(cleaned_date) >= 4 else None


def _ensureNumCharacters(s: str, numCharacters: int) -> str:
    """prepends 0 to string to ensure there are numCharacters characters present in the string"""
    if len(s) >= numCharacters:
        return s
    return "0" * (numCharacters - len(s)) + s


def is_date_in_YYYY_MM_DD(date: str) -> bool:
    if not date:
        return False
    pattern = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$")
    return bool(pattern.match(date[0]))


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
