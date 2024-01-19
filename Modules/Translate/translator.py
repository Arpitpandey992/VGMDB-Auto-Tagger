import subprocess
import cutlet
import json
from typing import Optional, get_args

# remove
import sys
import os

sys.path.append(os.getcwd())
# remove
from Imports.constants import TRANSLATE_LANGUAGES
from Modules.Translate.chatGPT import ChatGPTAPI
from Modules.Utils.general_utils import get_default_logger

logger = get_default_logger(__name__, "info")


# This uses 'translate-shell' system process for transcription. make sure it is available and added to path


def get_text_language(text: str) -> str:
    try:
        sourceLanguage = subprocess.run(["trans", "-identify", "-no-warn", text], capture_output=True, text=True).stdout.strip()
        return sourceLanguage.lower()
    except Exception as e:
        logger.exception(f"could not identify language: {e}")
    return ""


def translate_romaji(text: str) -> Optional[str]:
    def translate_google_translate(text: str) -> Optional[str]:
        options = ["trans", "--no-warn", "-t", "english", "-show-original", "Y", "-show-alternatives", "n", "-show-languages", "n", "-show-translation", "n", "-show-prompt-message", "n", "-no-theme", text]
        try:
            output_text = subprocess.run(options, capture_output=True, text=True).stdout.strip()
            lines = output_text.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("(") and line.endswith(")"):
                    return line[1:-1]
            return None

        except Exception as e:
            logger.exception(f"could not get romaji, error: {e}")
            return None

    def translate_romaji_cutlet(text: str) -> Optional[str]:
        katsu = cutlet.Cutlet()
        romajiText = katsu.romaji(text)
        return romajiText

    source_language = get_text_language(text)

    if source_language and "japanese" in source_language:
        logger.debug("using cutlet for translating to romaji")
        return translate_romaji_cutlet(text)

    logger.debug("using google translate for translating to romaji")
    return translate_google_translate(text)


def translate_translate_shell(text: str, target_language: str) -> str | None:
    def translate(text: str, target_language: str) -> Optional[str]:
        try:
            translated_text = subprocess.run(["trans", "-b", "-no-warn", "-t", target_language, text], capture_output=True, text=True).stdout.strip()
            return translated_text

        except Exception as e:
            logger.exception(f"could not translate, error: {e}")
            return None

    return translate(text, target_language)


def translate_chat_gpt(text: str, targetLanguage: str) -> str:
    def translate(text: str, targetLanguage: str):
        system_role = "You are a translation helper that is used to translate metadata of music files from one language to another."
        prompt = f"You will help to translate the given text to {targetLanguage}. The context for the text is: The given text is the title/name of a music track in a japanese soundtrack album. Try to be accurate and use plain english wherever appropriate. "
        if targetLanguage == "Romaji":
            prompt += "For english words present in text, written in japanese, write them out in plain english without any romanization. "
        prompt += f"Text:\n```\n{text}\n```"
        function_call = {
            "name": "show_translation_output",
            "description": "Show the output after translating the given text",
            "parameters": {
                "type": "object",
                "properties": {"translated_text": {"type": "string", "description": "text obtained after translation"}},
                "required": ["translated_text"],
            },
        }
        model_used = "4k_tokens_function_calling"
        response = ChatGPTAPI(
            model_name=model_used,
            system_role=system_role,
        ).query_with_function_call(
            prompt, function_call
        )["response"]
        responseDict = json.loads(response)
        return responseDict["translated_text"]

    options = {"text": text, "targetLanguage": targetLanguage}
    return translate(**options)


translate_cache: dict[tuple[str, TRANSLATE_LANGUAGES], str | None] = {}


def translate(text: str | None, target_language: TRANSLATE_LANGUAGES = "english") -> str | None:
    if not text:
        return
    global translate_cache
    if (text, target_language) in translate_cache:
        return translate_cache.get((text, target_language))
    source_language = get_text_language(text)
    if target_language.lower() in source_language or "english" in source_language:
        translate_cache[(text, target_language)] = None
        return None
    if target_language not in get_args(TRANSLATE_LANGUAGES):
        logger.error(f"{target_language} is not supported for translation")
        return None
    translated_text = None
    if target_language == "romaji":
        # chatGPT is good for romaji, but API KEY :(
        use_chat_gpt = False
        if use_chat_gpt:
            try:
                translated_text = translate_chat_gpt(text, "Romaji")
            except Exception as e:
                logger.error(f"chatGPT failed for {text}, using cutlet")
                logger.debug(f"error:\n{e}")
                translated_text = translate_romaji(text)
        else:
            translated_text = translate_romaji(text)
    else:
        translated_text = translate_translate_shell(text, target_language)
    translate_cache[(text, target_language)] = translated_text
    return translated_text


if __name__ == "__main__":
    target_languages: list[TRANSLATE_LANGUAGES] = ["english", "romaji"]
    examples = [
        "Damn son, this is in english",
        "醉梦前尘 - 琵琶版",
        "18 - 神魔战.ogg",
        "届かぬ恋",
        "17 - 星座開設 「星を読む」.flac",
        "08 - 雪圏球 -Under the Snow",
        "雪圏球 -Under the Snow",
        "you -卒業- feat.島みやえいこ",
        "11 - 乾涸びたバスひとつ",
        "8 - little_thing -キコニアのなく頃に 未使用曲-",
        "02 - Hurry, Starfish -PaPiPuPe Mix-",
        "時を刻む唄",
        "あの日へ繋がるラジオ",
        "Thanks -fromˮCD꞉yoursˮ2022マスタリングVer.- feat.癒月",
    ]
    for i in range(2):
        for example in examples:
            print(f"original: {example}")
            for target_language in target_languages:
                print(f"{target_language}: {translate(example,target_language)}")
            print("------------------------------")
