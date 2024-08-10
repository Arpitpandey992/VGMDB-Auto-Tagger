import os
import random
import shutil
import string
from typing import Any

currentFileAbsolutePath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
baseFolder = os.path.join(currentFileAbsolutePath, "testSamples", "baseSamples")
modifiedFolder = os.path.join(currentFileAbsolutePath, "testSamples", "modifiedSamples")
coversPath = os.path.join(baseFolder, "covers")
covers = [os.path.join(coversPath, coverName) for coverName in os.listdir(coversPath)]

# Unicode range for common Japanese characters (Hiragana, Katakana, and common Kanji)
japanese_chars = [
    (0x3041, 0x3096),  # Hiragana
    (0x30A1, 0x30F6),  # Katakana
    (0x4E00, 0x9FBF),  # Common Kanji
]
all_japanese_chars = "".join(chr(x) for x in [k for start, end in japanese_chars for k in range(start, end)])
supported_extensions = ["flac", "mp3", "m4a", "wav", "ogg", "opus"]


def getRandomCoverImageData() -> bytes:
    num_covers = len(covers)
    cover_index = random.randrange(0, num_covers, 1)
    path = covers[cover_index]
    # del covers[cover_index]
    with open(path, "rb") as image_file:
        image_data = image_file.read()
    return image_data


def generate_random_string(size_lower_limit: int, size_upper_limit: int):
    string_size = random.randint(size_lower_limit, size_upper_limit)
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(string_size))
    return random_string


def generate_random_japanese_string(size_lower_limit: int, size_upper_limit: int) -> str:
    siz = random.randint(size_lower_limit, size_upper_limit)
    random_string = "".join(random.choice(all_japanese_chars) for _ in range(siz))
    return random_string


def generate_random_list_containing_random_strings(list_size_lower_limit: int, list_size_upper_limit: int, string_size_lower_limit: int, string_size_upper_limit: int):
    list_size = random.randint(list_size_lower_limit, list_size_upper_limit)
    return [generate_random_string(string_size_lower_limit, string_size_upper_limit) if random.randint(0, 1) == 0 else generate_random_japanese_string(string_size_lower_limit, string_size_upper_limit) for _ in range(list_size)]


def select_random_keys_from_list(arr: list[Any]) -> list[Any]:
    num_keys_to_select = random.randint(2, len(arr))
    return random.sample(arr, num_keys_to_select)


def generate_random_number_between_inclusive(l: int, r: int) -> int:
    return random.randint(l, r)


def copy_base_samples(force: bool = False):
    # print("copying base samples to modified folder")
    if os.path.exists(modifiedFolder):
        shutil.rmtree(modifiedFolder)
    os.makedirs(modifiedFolder, exist_ok=True)
    for file in os.listdir(baseFolder):
        file_path = os.path.join(baseFolder, file)
        modified_file_path = os.path.join(modifiedFolder, file)
        if not force and os.path.exists(modified_file_path):
            continue
        if os.path.isfile(file_path):
            shutil.copy(file_path, modifiedFolder)


def get_test_file_path(file_extension: str) -> str:
    file_extension = file_extension.lower()
    if file_extension not in supported_extensions:
        raise Exception(f"{file_extension} is not supported")
    return os.path.join(modifiedFolder, f"{file_extension}_test.{file_extension}")


def save_image(image_bytes: bytes, filename: str):
    """
    Save image bytes to a file.

    :param image_bytes: Bytes representing the image.
    :param filename: Name of the file to save the image as.
    """
    try:
        with open(filename, "wb") as img_file:
            img_file.write(image_bytes)
        print(f"Image saved as {filename}.")
    except Exception as e:
        print(f"Error saving image: {e}")
