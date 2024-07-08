# REMOVE
import os
import sys

sys.path.append(os.getcwd())
# REMOVE
from Modules.Mutagen.audio_factory import AudioFactory

filePath = "/mnt/c/Users/Arpit/Downloads/m4a_test.m4a"


audiofile = AudioFactory.buildAudioManager(filePath)
info = audiofile.getInfo()

print(info)
