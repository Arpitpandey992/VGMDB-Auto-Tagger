import requests
import io
from PIL import Image

from Imports.flagsAndSettings import Flags
from Utility.utilityFunctions import getBest, getProperCount
from Utility.mutagenWrapper import AudioFactory


def standardizeDate(date) -> str:
    if date is None:
        return ""
    dateComponents = date.split('-')
    numberOfComponents = len(dateComponents)

    if numberOfComponents == 1:
        date = date + '-00-00'
    elif numberOfComponents == 2:
        date = date + '-00'
    else:
        pass
    return date


def getImageData(data):
    if 'pictureCache' in data:
        return data['pictureCache']
    if 'picture_full' not in data:
        return None

    response = requests.get(data['picture_full'])
    imageData = response.content
    image = Image.open(io.BytesIO(imageData))
    image = image.convert('RGB')  # Remove transparency if present
    width, height = image.size

    if width > 800:
        new_height = int(height * (800 / width))
        image = image.resize((800, new_height), resample=Image.LANCZOS)

    imageData = io.BytesIO()
    image.save(imageData, format='JPEG', quality=70)
    imageData = imageData.getvalue()
    data['pictureCache'] = imageData
    return imageData


def tagAudioFile(data, albumData):
    flags: Flags = data['flags']
    audio = AudioFactory.buildAudioManager(albumData['filePath'])

    # Tagging Album specific Details
    if flags.TITLE:
        audio.setTitle(albumData['trackTitle'])
    audio.setAlbum(albumData['albumName'])
    audio.setTrackNumbers(getProperCount(albumData['trackNumber'], albumData['totalTracks']),
                          str(albumData['totalTracks']))
    audio.setDiscNumbers(getProperCount(albumData['discNumber'], albumData['totalDiscs']),
                         str(albumData['totalDiscs']))
    audio.setComment(f"Find the tracklist at {data['albumLink']}")

    if flags.PICS:
        imageData = getImageData(data)
        if imageData is not None:
            if audio.hasPictureOfType(3):
                if flags.PIC_OVERWRITE:
                    audio.deletePictureOfType(3)
                    audio.setPictureOfType(imageData, 3)
            else:
                audio.setPictureOfType(imageData, 3)

    if flags.DATE and 'release_date' in data:
        audio.setDate(standardizeDate(data['release_date']))

    if flags.YEAR and 'release_date' in data and len(data['release_date']) >= 4:
        audio.setCustomTag('Year', data['release_date'][0:4])

    if flags.CATALOG and 'catalog' in data:
        audio.setCatalog(data['catalog'])

    if flags.BARCODE and 'barcode' in data:
        audio.setCustomTag('Barcode', data['barcode'])

    if flags.ORGANIZATIONS and 'organizations' in data:
        for org in data['organizations']:
            audio.setCustomTag(org['role'], getBest(org['names'], flags.languageOrder))

    def addMultiValues(tag, tagInFile, flag=True):
        if tag in data and flag:
            listOfValues = []
            for val in data[tag]:
                listOfValues.append(getBest(val['names'], flags.languageOrder))
            audio.addMultipleValues(tagInFile, listOfValues)

    addMultiValues('lyricists', 'lyricist', flags.LYRICISTS)
    addMultiValues('performers', 'performer', flags.PERFORMERS)
    addMultiValues('arrangers', 'arranger', flags.ARRANGERS)
    addMultiValues('composers', 'composer', flags.COMPOSERS)

    try:
        audio.save()
        return True
    except Exception as e:
        print(e)
    return False
