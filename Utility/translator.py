import subprocess
from typing import Optional
from typing_extensions import TypedDict
import cutlet


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
        print(f'Could not identify language - {e}')
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
        print(f'Could not translate - {e}')
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
        print(f'Could not get romaji - {e}')
        return None


def _getRomajiCutlet(text: str) -> Optional[str]:
    katsu = cutlet.Cutlet()
    romajiText = katsu.romaji(text)
    return romajiText


def getRomaji(text: str, languageText: Optional[str] = None) -> Optional[str]:
    if languageText and 'japanese' in languageText:
        return _getRomajiCutlet(text)
    return _getRomajiGoogleTranslate(text)


def translateShell(text: str, targetLanguage: str) -> TranslateResponse:
    sourceLanguage = getLanguageInfo(text)
    if sourceLanguage and targetLanguage in sourceLanguage:
        # No need to translate
        translatedText = None
    else:
        translatedText = getTranslation(text, targetLanguage)
    romajiText = getRomaji(text, sourceLanguage)

    return {
        "translatedText": translatedText,
        "romajiText": romajiText
    }


def translate(text: str, targetLanguage: str = 'english') -> TranslateResponse:
    """targetLanguage must be full language name, like Hindi, English, Japanses, etc (not abbreviation)"""
    return translateShell(text, targetLanguage.lower().strip())


if __name__ == '__main__':
    print(translate('醉梦前尘 - 琵琶版'))
    print(translate('18 - 神魔战.ogg'))
    print(translate('届かぬ恋'))
    print(translate('17 - 星座開設 「星を読む」.flac'))
    print(translate('08 - 雪圏球 -Under the Snow'))
    print(translate('雪圏球 -Under the Snow'))
    print(translate('you -卒業- feat.島みやえいこ'))
    print(translate('11 - 乾涸びたバスひとつ'))
    print(translate('13 - little_thing -キコニアのなく頃に 未使用曲-'))
