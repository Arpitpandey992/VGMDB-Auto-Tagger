import subprocess
from typing import Optional
from typing_extensions import TypedDict
import cutlet
import json

from Modules.Translate.chatGPT import ChatGPTAPI
from Modules.Utils.general_utils import get_default_logger

logger = get_default_logger(__name__, 'info')


# This uses 'translate-shell' system process for transcription. make sure it is available and added to path
class TranslateResponse(TypedDict):
    translatedText: Optional[str]
    romajiText: Optional[str]


def getLanguageInfo(text: str) -> Optional[str]:
    try:
        sourceLanguage = subprocess.run(
            ['trans', '-identify', '-no-warn', text],
            capture_output=True,
            text=True
        ).stdout.strip()
        return sourceLanguage.lower()
    except Exception as e:
        logger.exception(f'could not identify language: {e}')
        return None


def getTranslation(text: str, targetLanguage: str) -> Optional[str]:
    try:
        translatedText = subprocess.run(
            ['trans', '-b', '-no-warn',
             '-t', targetLanguage, text],
            capture_output=True,
            text=True
        ).stdout.strip()

        return translatedText

    except Exception as e:
        logger.exception(f'could not translate, error: {e}')
        return None


def _getRomajiGoogleTranslate(text: str) -> Optional[str]:
    options = ['trans', '--no-warn', '-t', 'english', '-show-original', 'Y', '-show-alternatives', 'n',
               '-show-languages', 'n', '-show-translation', 'n', '-show-prompt-message', 'n', '-no-theme', text]
    try:
        output_text = subprocess.run(
            options,
            capture_output=True,
            text=True
        ).stdout.strip()
        lines = output_text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith('(') and line.endswith(')'):
                return line[1:-1]
        return None

    except Exception as e:
        logger.exception(f'could not get romaji, error: {e}')
        return None


def _getRomajiCutlet(text: str) -> Optional[str]:
    katsu = cutlet.Cutlet()
    romajiText = katsu.romaji(text)
    return romajiText


def getRomaji(text: str, languageText: Optional[str] = None) -> Optional[str]:
    if languageText and 'japanese' in languageText:
        return _getRomajiCutlet(text)
    return _getRomajiGoogleTranslate(text)


def translateShell(text: str, targetLanguage: str) -> str:
    sourceLanguage = getLanguageInfo(text)
    if sourceLanguage and targetLanguage in sourceLanguage:
        # No need to translate
        translatedText = None
    else:
        translatedText = getTranslation(text, targetLanguage)

    return translatedText if translatedText else ""


def translateChatGPT(text: str, targetLanguage: str):
    system_role = "You are a translation helper that is used to translate metadata of music files from one language to another."
    prompt = f'You will help to translate the given text to {targetLanguage}. The context for the text is: The given text is the title/name of a music track in a japanese soundtrack album. Try to be accurate and use plain english wherever appropriate. '
    if targetLanguage == 'Romaji':
        prompt += 'For english words present in text, written in japanese, write them out in plain english without any romanization. '
    prompt += f'Text:\n```\n{text}\n```'
    function_call = {
        "name": "show_translation_output",
        "description": "Show the output after translating the given text",
        "parameters": {
                "type": "object",
                "properties": {
                    "translated_text": {
                        "type": "string",
                        "description": "text obtained after translation"
                    }
                },
            "required": ["translated_text"],
        },
    }
    model_used = "4k_tokens_function_calling"
    response = ChatGPTAPI(
        model_name=model_used,
        system_role=system_role,
    ).query_with_function_call(prompt, function_call)["response"]
    responseDict = json.loads(response)
    return responseDict["translated_text"]


def translateGPT(text: str, targetLanguage: str):
    options = {
        "text": text,
        "targetLanguage": targetLanguage
    }
    return translateChatGPT(**options)


def translate(text: str, targetLanguage: str = 'english', textType: Optional[str] = None) -> TranslateResponse:
    """targetLanguage must be full language name, like Hindi, English, Japanese, etc (not abbreviation)"""
    translatedText = translateShell(text, targetLanguage.lower().strip())
    # chatGPT is good for romaji
    useChatGPT = False
    if useChatGPT:
        try:
            romajiText = translateGPT(text, "Romaji")
        except Exception as e:
            logger.error(f"chatGPT failed for {text}, using cutlet")
            sourceLanguage = getLanguageInfo(text)
            romajiText = getRomaji(text, sourceLanguage)
    else:
        sourceLanguage = getLanguageInfo(text)
        romajiText = getRomaji(text, sourceLanguage)

    return {
        "translatedText": translatedText,
        "romajiText": romajiText
    }


if __name__ == '__main__':
    # print(translate('醉梦前尘 - 琵琶版'))
    # print(translate('18 - 神魔战.ogg'))
    # print(translate('届かぬ恋'))
    # print(translate('17 - 星座開設 「星を読む」.flac'))
    # print(translate('08 - 雪圏球 -Under the Snow'))
    # print(translate('雪圏球 -Under the Snow'))
    # print(translate('you -卒業- feat.島みやえいこ'))
    # print(translate('11 - 乾涸びたバスひとつ'))
    # print(translate('8 - little_thing -キコニアのなく頃に 未使用曲-'))
    # print(translate('02 - Hurry, Starfish -PaPiPuPe Mix-'))
    # print(translate('時を刻む唄'))
    print(translate('あの日へ繋がるラジオ'))
    print(translate('Thanks -fromˮCD꞉yoursˮ2022マスタリングVer.- feat.癒月'))
