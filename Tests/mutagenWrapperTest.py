import os
import sys
import traceback
import random
sys.path.append(os.getcwd())
from Utility.mutagenWrapper import AudioFactory, IAudioManager

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
baseFolder = os.path.join(__location__, "testSamples")
coversPath = os.path.join(baseFolder, "covers")
covers = [os.path.join(coversPath, coverName) for coverName in os.listdir(coversPath)]
SEE_PASSED = False


def getRandomCover():
    num_covers = len(covers)
    cover_index = random.randrange(0, num_covers, 1)
    path = covers[cover_index]
    del covers[cover_index]
    return path


def testMutagenWrapper(audio: IAudioManager):
    # Test setting and getting title
    try:
        audio.setTitle(["New Title"])
        assert audio.getTitle() == "New Title"
        if SEE_PASSED:
            print("setTitle and getTitle test passed")
    except Exception as e:
        print("setTitle and getTitle test Failed:\n")
        traceback.print_exc()
        print('')

    # Test setting and getting album
    try:
        audio.setAlbum(["New Album"])
        assert audio.getAlbum() == "New Album"
        if SEE_PASSED:
            print("setAlbum and getAlbum test passed")
    except Exception as e:
        print("setAlbum and getAlbum test Failed:\n")
        traceback.print_exc()
        print('')

    # Test setting and getting disc numbers
    try:
        audio.setDiscNumbers("1", "2")
        assert audio.getDiscNumber() == "1"
        assert audio.getTotalDiscs() == "2"
        if SEE_PASSED:
            print("setDiscNumbers, getDiscNumber and getTotalDiscs test passed")
    except Exception as e:
        print("setDiscNumbers, getDiscNumber and getTotalDiscs test Failed:\n")
        traceback.print_exc()
        print('')

    # Test setting and getting track numbers
    try:
        audio.setTrackNumbers("1", "10")
        assert audio.getTrackNumber() == "1"
        assert audio.getTotalTracks() == "10"
        if SEE_PASSED:
            print("setTrackNumbers, getTrackNumber and getTotalTracks test passed")
    except Exception as e:
        print("setTrackNumbers, getTrackNumber and getTotalTracks test Failed:\n")
        traceback.print_exc()
        print('')

    # Test setting and getting comment
    try:
        audio.setComment("This is a comment")
        assert audio.getComment() == "This is a comment"
        if SEE_PASSED:
            print("setComment and getComment test passed")
    except Exception as e:
        print("setComment and getComment test Failed:\n")
        traceback.print_exc()
        print('')

    # Test setting and getting album release date
    try:
        audio.setDate("2022-01-01")
        assert audio.getDate() == "2022-01-01"
        if SEE_PASSED:
            print("setDate and getDate test passed")
    except Exception as e:
        print("setDate and getDate test Failed:\n")
        traceback.print_exc()
        print('')

    # Test setting and getting Catalog
    try:
        audio.setCatalog("KSLA-01022")
        assert audio.getCatalog() == "KSLA-01022"
        if SEE_PASSED:
            print("setCatalog and getCatalog test passed")
    except Exception as e:
        print("setCatalog and getCatalog test Failed:\n")
        traceback.print_exc()
        print('')
    # Test setting and getting custom tags
    try:
        audio.setCustomTag("MY_TAG", "my_value")
        assert audio.getCustomTag("MY_TAG") == "my_value"
        if SEE_PASSED:
            print("setCustomTag and getCustomTag test passed")
    except Exception as e:
        print("setCustomTag and getCustomTag test Failed:\n")
        traceback.print_exc()
        print('')

    # Test setting and getting disc name
    try:
        audio.setDiscName("Disc 1")
        assert audio.getDiscName() == "Disc 1"
        if SEE_PASSED:
            print("setDiscName and getDiscName test passed")
    except Exception as e:
        print("setDiscName and getDiscName test Failed:\n")
        traceback.print_exc()
        print('')

    # Test getting information
    try:
        info = audio.getInformation()
        assert isinstance(info, str)
        if SEE_PASSED:
            print("getInformation test passed")
    except Exception as e:
        print("getInformation test Failed:\n")
        traceback.print_exc()
        print('')

    try:
        # read the image file
        with open(getRandomCover(), 'rb') as image_file:
            image_data = image_file.read()

        # set the picture of type 3
        audio.setPictureOfType(image_data, 3)

        # check if the picture exists
        assert audio.hasPictureOfType(3) == True

        # delete the picture
        audio.deletePictureOfType(3)

        # check if the picture was deleted
        assert audio.hasPictureOfType(3) == False

        # set and check again
        audio.setPictureOfType(image_data, 3)

        # check if the picture exists
        assert audio.hasPictureOfType(3) == True

    except AssertionError as e:
        print("cover related tests Failed:\n")
        traceback.print_exc()
        print('')

     # Test saving changes
    try:
        audio.save()
        if SEE_PASSED:
            print("save test passed")
    except Exception as e:
        print("save test Failed:\n")
        traceback.print_exc()
        print('')


extensions = ["flac", "mp3", "m4a", "wav", "ogg", "opus"]
for extension in extensions:
    print(f"Testing {extension} file")
    filePath = os.path.join(baseFolder, f"{extension}_test.{extension}")
    testMutagenWrapper(AudioFactory.buildAudioManager(filePath))
