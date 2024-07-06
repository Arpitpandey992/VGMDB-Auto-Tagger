import os
from Modules.Mutagen.id3 import ID3Wrapper
from Modules.Mutagen.mp4 import MP4Wrapper
from Modules.Mutagen.audio_manager import IAudioManager
from Modules.Mutagen.vorbis import VorbisWrapper


audioFileHandler = {
    ".flac": VorbisWrapper,
    ".wav": ID3Wrapper,
    ".mp3": ID3Wrapper,
    ".ogg": VorbisWrapper,
    ".opus": VorbisWrapper,
    ".m4a": MP4Wrapper,
}
supportedExtensions = audioFileHandler.keys()


def isFileFormatSupported(filePath: str) -> bool:
    _, extension = os.path.splitext(filePath)
    return extension.lower() in supportedExtensions


class AudioFactory:
    @staticmethod
    def buildAudioManager(filePath: str) -> IAudioManager:
        if not isFileFormatSupported(filePath):
            raise UnsupportedFileFormatError(filePath)
        _, extension = os.path.splitext(filePath)
        extension = extension.lower()
        codec = audioFileHandler[extension]
        return codec(filePath, extension)  # type: ignore


class UnsupportedFileFormatError(Exception):
    def __init__(self, file_path: str):
        self.file_path = file_path
        message = f"unsupported file format for the file: {file_path}"
        super().__init__(message)


if __name__ == "__main__":
    filePath = "/Users/arpit/Library/Custom/Downloads/example.mp3"
    audio = AudioFactory.buildAudioManager(filePath)
    print(type(audio))
    audio.setCustomTag("yourssss", ["yepyep", "ei", "213dasfdad"])
    audio.setTitle(["damn", "sons", "huh"])
    audio.setComment(["This is a comment", "This as well", "maybe this one too ;)"])
    audio.save()
    print(audio.printInfo())
