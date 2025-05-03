import cutlet
import json
import langid
from enum import Enum
from typing import Literal
from translate_shell.translate import translate as translate_shell_translate

# remove
import sys
import os

sys.path.append(os.getcwd())
# remove
from Modules.Translate.chatGPT import ChatGPTAPI
from Modules.Utils.general_utils import get_default_logger

LANGUAGE_NAME = Literal["english", "romaji", "chinese", "hindi", "japanese"]


class Language(Enum):
    english = "en"
    japanese = "ja"
    chinese = "zh"
    hindi = "hi"
    # custom languages which are not present in ISO 639 codes
    romaji = "rom"

    @classmethod
    def from_value(cls, value: str):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a supported {cls.__name__}")

    @classmethod
    def from_language_name(cls, language_name: LANGUAGE_NAME):
        language_name_mapping = cls.get_language_name_mapping()
        if language_name in language_name_mapping:
            return language_name_mapping[language_name]
        # Ideally it should never go beyond this point
        raise ValueError(f"{language_name} is not a supported {cls.__name__}")

    @classmethod
    def is_valid_language(cls, lang: str) -> bool:
        for member in cls:
            if member.value == lang:
                return True
        return False

    def to_language_name(self) -> str:
        language_name_mapping = Language.get_language_name_mapping()
        for language_name, language_enum in language_name_mapping.items():
            if language_enum == self.name:
                return language_name
        raise ValueError(f"{self.name}:{self.value} enum could not be converted to language name")

    @classmethod
    def get_language_name_mapping(cls) -> dict[LANGUAGE_NAME, "Language"]:
        return {"english": cls.english, "japanese": cls.japanese, "chinese": cls.chinese, "hindi": cls.hindi, "romaji": cls.romaji}


class Translator:
    TRANSLATOR = Literal["cutlet", "chatgpt", "translate-shell"]
    ROMAJI_TRANSLATOR: TRANSLATOR = "cutlet"
    GENERAL_TRANSLATOR: TRANSLATOR = "translate-shell"

    def __init__(self):
        self.logger = get_default_logger(__name__, "info")
        self.translate_cache: dict[tuple[str, LANGUAGE_NAME], str | None] = {}

    def translate(self, text: str | None, target_language_name: LANGUAGE_NAME = "english") -> str | None:
        if not text or not text.strip():
            self.logger.exception(f"empty text provided for translation, skipping")
            return None

        if (text, target_language_name) in self.translate_cache:
            self.logger.debug(f"using cached translation entry for translating: {text} to: {target_language_name}")
            return self.translate_cache.get((text, target_language_name))

        self.logger.debug(f"translating {text} to {target_language_name}")

        target_language = Language.from_language_name(target_language_name)
        source_language = self._identify_language(text)

        if source_language == Language.english or source_language == target_language:
            self.logger.debug(f"no need to translate: {text} to {target_language_name}")
            self.translate_cache[(text, target_language_name)] = None
            return None

        translated_text = None
        try:
            if target_language == Language.romaji:
                translated_text = self._translate_to_romaji(text)
            else:
                translated_text = self._general_translation(text, target_language)
        except Exception as e:
            raise Exception(f"could not translate {text} to {target_language_name}. exception: {e}")

        if translated_text is not None:
            self.translate_cache[(text, target_language_name)] = translated_text
        return translated_text

    def _general_translation(self, text: str, target_language: Language) -> str:
        if self.GENERAL_TRANSLATOR == "chatgpt":
            self.logger.debug("using chatGPT for translation")
            return self._translate_using_chat_gpt(text, target_language)

        self.logger.debug("using translate-shell for translation")
        return self._translate_using_translate_shell(text, target_language)

    def _translate_to_romaji(self, text: str) -> str:
        if self.ROMAJI_TRANSLATOR == "cutlet":
            source_language = self._identify_language(text)
            if source_language == Language.japanese:
                self.logger.debug("using cutlet for translation")
                return self._translate_to_romaji_using_cutlet(text)
        elif self.ROMAJI_TRANSLATOR == "chatgpt":
            self.logger.debug("using chatGPT for translation")
            return self._translate_using_chat_gpt(text, Language.romaji)

        self.logger.debug("using translate-shell for translation")
        return self._translate_to_romaji_using_translate_shell(text)

    # <Source Lang> -> <Target Lang> translation
    def _translate_using_translate_shell(self, text: str, target_language: Language) -> str:
        translated_text = translate_shell_translate(text, target_lang=target_language.value)
        if translated_text.status != 1 or len(translated_text.results) == 0:
            raise Exception(f"could not translate {text} to {target_language} using translate-shell")
        result = translated_text.results[0]
        return result.paraphrase

    # It can do both general purpose translation and romaji translation
    def _translate_using_chat_gpt(self, text: str, target_language: Language) -> str:
        system_role = "You are a translation helper that is used to translate metadata of music files from one language to another."
        prompt = f"You will help to translate the given text to {target_language.name}. The context for the text is: The given text is the title/name of a music track in a japanese soundtrack album. Try to be accurate and use plain english wherever appropriate. "
        if target_language == Language.romaji:
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
        response = ChatGPTAPI(
            system_role=system_role,
        ).query_with_function_call(
            prompt, function_call
        )["response"]
        responseDict = json.loads(response)
        return responseDict["translated_text"]

    # <Source Lang> -> Romaji translation
    def _translate_to_romaji_using_translate_shell(self, text: str) -> str:
        translated_text = translate_shell_translate(text)
        if translated_text.status != 1 or len(translated_text.results) == 0:
            raise Exception(f"could not translate {text} to {target_language} using translate-shell")
        result = translated_text.results[0]
        return result.phonetic

    def _translate_to_romaji_using_cutlet(self, text: str) -> str:
        """only from ja -> rom translation"""
        katsu = cutlet.Cutlet()
        romajiText = katsu.romaji(text)
        if not romajiText:
            raise Exception(f"could not translate {text} to romaji using cutlet")
        return romajiText

    def _identify_language(self, text: str) -> Language:
        result = langid.classify(text)
        if not result:
            raise Exception(f"could not identify language for text: {text}")
        identified_language = result[0].lower().strip()
        if Language.is_valid_language(identified_language):
            return Language.from_value(identified_language)
        raise Exception(f"identified language: {identified_language} is not a supported Language")


if __name__ == "__main__":
    target_languages: list[LANGUAGE_NAME] = ["english", "romaji"]
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
    translator = Translator()
    for i in range(2):
        for example in examples:
            print(f"original: {example}")
            for target_language in target_languages:
                print(f"{target_language}: {translator.translate(example,target_language)}")
            print("------------------------------")
