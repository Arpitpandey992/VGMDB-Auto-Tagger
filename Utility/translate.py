import subprocess

# This uses 'translate-shell' system process to do the task. make sure it is available and added to path


def _translate_translate_shell(oldText: str, target_language: str = 'en') -> str:
    try:
        language = subprocess.run(
            ['trans', '-identify', '-no-warn', oldText],
            capture_output=True,
            text=True
        ).stdout.strip()
        if 'English' in language:
            return oldText
        translated_text = subprocess.run(
            ['trans', '-b', '-no-warn'
                f':{target_language}', oldText],
            capture_output=True,
            text=True
        ).stdout.strip()

        return translated_text
    except Exception as e:
        print(f'Could not translate - {e}')
        return oldText


def translate(text: str) -> str:
    return _translate_translate_shell(text)


if __name__ == '__main__':
    print(translate('醉梦前尘 - 琵琶版'))
    print(translate('18 - 神魔战.ogg'))
    print(translate('届かぬ恋'))
    print(translate('17 - 星座開設 「星を読む」.flac'))
    print(translate('08 - 雪圏球 -Under the Snow'))
    print(translate('雪圏球 -Under the Snow'))
