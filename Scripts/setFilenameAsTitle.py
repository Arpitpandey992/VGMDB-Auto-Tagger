import os
import sys

sys.path.append(os.getcwd())
from Modules.Mutagen.audio_factory import AudioFactory


folderPath = ""

for dirpath, dirnames, filenames in os.walk(folderPath):
    for filename in filenames:
        if filename.endswith(".mp3"):
            fileName, _ = os.path.splitext(filename)
            file_path = os.path.join(dirpath, filename)
            audio = AudioFactory.buildAudioManager(file_path)
            title = audio.getTitle()
            if not title:
                print(f"{fileName} title set")
                audio.setTitle([fileName])
                audio.save()
