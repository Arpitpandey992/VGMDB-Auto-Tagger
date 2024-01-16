import os
import sys
import logging
from typing import Union, Optional
from math import ceil, log10
from dotenv import load_dotenv

load_dotenv()


def get_default_logger(name: str, logging_level="info") -> logging.Logger:
    logging_levels = {"info": logging.INFO, "debug": logging.DEBUG, "error": logging.ERROR, "critical": logging.CRITICAL, "fatal": logging.FATAL}
    if logging_level not in logging_levels:
        raise Exception(f'invalid logging level: {logging_level}, choose among {", ".join(logging_levels.keys())}')
    level = logging_levels[logging_level]
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


def yesNoUserInput() -> bool:
    print("Continue? (Y/n) : ", end="")
    resp = input()
    if resp == "n" or resp == "N":
        return False
    return True


def noYesUserInput() -> bool:
    print("Continue? (y/N) : ", end="")
    resp = input()
    if resp == "y" or resp == "Y":
        return True
    return False


forbiddenCharacters = {
    "<": "ᐸ",
    ">": "ᐳ",
    ":": "꞉",
    '"': "ˮ",
    "'": "ʻ",
    # '/': '／', # Looks far too stretched, but is more popular for some reason
    "/": "Ⳇ",  # This one looks more natural
    "\\": "∖",
    "|": "ǀ",
    "?": "ʔ",
    "*": "∗",
    "+": "＋",
    "%": "٪",
    "!": "ⵑ",
    "`": "՝",
    "&": "&",  # keeping same as it is not forbidden, but it may cause problems
    "{": "❴",
    "}": "❵",
    "=": "᐀",
    "~": "～",  # Not using this because it could be present in catalog number as well, may cause problems though
    "#": "#",  # couldn't find alternative
    "$": "$",  # couldn't find alternative
    "@": "@",  # couldn't find alternative
}


def cleanName(name: str) -> str:
    output = name.strip()
    for invalidCharacter, validAlternative in forbiddenCharacters.items():
        output = output.replace(invalidCharacter, validAlternative)
    return output


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

    def isJapanese(ch):
        return ord(ch) >= 0x4E00 and ord(ch) <= 0x9FFF

    def isChinese(ch):
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
