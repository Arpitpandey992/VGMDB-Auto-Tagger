import os
from mutagenWrapper import AudioFactory, supportedExtensions


def cleanName(name: str):
    forbiddenCharacters = {
        '<': 'ᐸ',
        '>': 'ᐳ',
        ':': '꞉',
        '"': 'ˮ',
        '\'': 'ʻ',
        '/': '／',
        '\\': '∖',
        '|': 'ǀ',
        '?': 'ʔ',
        '*': '∗',
        '+': '᛭',
        '%': '٪',
        '!': 'ⵑ',
        '`': '՝',
        '&': '&',  # keeping same as it is not forbidden, but it may cause problems
        '{': '❴',
        '}': '❵',
        '=': '᐀',
        # Not using this because it could be present in catalog number as well, may cause problems though
        # '~': '～',
        '#': '#',  # couldn't find alternative
        '$': '$',  # couldn't find alternative
        '@': '@'  # couldn't find alternative
    }
    output = name
    for invalidCharacter, validAlternative in forbiddenCharacters.items():
        output = output.replace(invalidCharacter, validAlternative)
    return output


folderPath = "/run/media/arpit/DATA/Music/Japanese"

for file in os.listdir(folderPath):
    _, ext = os.path.splitext(file)
    if (ext not in supportedExtensions):
        continue
    filePath = os.path.join(folderPath, file)
    audio = AudioFactory.buildAudioManager(filePath)
    title = audio.getTitle()
    artist = audio.getArtist()
    if (title and artist):
        newName = f"{artist} - {title}{ext}"
    elif title:
        newName = title+ext
    else:
        continue
    newName = cleanName(newName)
    if (file != newName):
        os.rename(filePath, os.path.join(folderPath, newName))
        print(f"Renamed {file} to {newName}")
