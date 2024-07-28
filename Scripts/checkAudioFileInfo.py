from unigen import AudioFactory

filePath = "/mnt/c/Users/Arpit/Downloads/m4a_test.m4a"


audiofile = AudioFactory.buildAudioManager(filePath)
info = audiofile.getInfo()

print(info)
