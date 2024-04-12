import hashlib
import os
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


def getProperCount(count: Union[str, int], totalCount: Union[str, int]) -> str:
    # if total tracks = 100, then this function will convert 1 to 001 for consistent sorting
    try:
        upperBound = int(ceil(log10(int(totalCount) + 1)))
        return str(count).zfill(upperBound)
    except Exception as e:
        logger.exception(e)

    return str(count)


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
