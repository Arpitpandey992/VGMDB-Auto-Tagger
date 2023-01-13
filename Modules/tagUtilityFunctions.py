import requests
import io
from mutagen.flac import Picture as FLAC_PICTURE, FLAC
from mutagen.id3._frames import APIC as MP3_PICTURE
from PIL import Image

from Modules.flagsAndSettings import *
from Modules.utilityFunctions import getBest

# data should contain 'picture_full' and extension should be like .<ext_name> (eg: .flac, .mp3, ...)

supportedExtensions = ['.flac', '.mp3']


def hasCoverOfType(audio, pictureType, extension):
    if extension == '.flac':
        for picture in audio.pictures:
            if picture.type == pictureType:
                return True
        return False

    elif extension == '.mp3':
        pictures = audio.getall("APIC")
        if pictures:
            for picture in pictures:
                if picture.type == pictureType:
                    return True
        return False

    return False


def standardize_date(date_string: str) -> str:
    # Split the date string into its components
    date_components = date_string.split('-')
    num_components = len(date_components)

    if num_components == 1:
        date_string = date_string + '-00-00'
    elif num_components == 2:
        date_string = date_string + '-00'
    else:
        pass
    return date_string


def getPictureObject(data, extension):
    if extension not in supportedExtensions:
        return None

    # removing . (assuming input is like .flac, .mp3)
    extension = extension[1:].lower()
    pictureKey = f'picture_{extension}'
    if pictureKey in data:
        return data[pictureKey]
    if 'picture_full' not in data:
        return None

    response = requests.get(data['picture_full'])
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))
    image = image.convert('RGB')  # Remove transparency if present
    width, height = image.size

    if width > 800:
        new_height = int(height * (800 / width))
        image = image.resize((800, new_height), resample=Image.LANCZOS)

    image_data = io.BytesIO()
    image.save(image_data, format='JPEG', quality=70)
    image_data = image_data.getvalue()

    # creating Mutagen Object
    if extension == 'flac':
        picture = FLAC_PICTURE()
        picture.data = image_data
        picture.type = 3
        picture.mime = 'image/jpeg'
        data[pictureKey] = picture
        return picture

    elif extension == 'mp3':
        picture = MP3_PICTURE(encoding=3,
                              mime='image/jpeg',
                              type=3,
                              desc=u'Cover (Front)',
                              data=image_data)
        data[pictureKey] = picture
        return picture


def tagFLAC(data, albumData):
    flags: Flags = data['flags']
    audio = FLAC(albumData['filePath'])
    # Tagging Album specific Details

    if flags.DATE and 'release_date' in data:
        audio['date'] = standardize_date(data['release_date'])

    audio['album'] = albumData['albumName']
    picture = getPictureObject(data, albumData['extension'])
    if flags.PICS and picture is not None:
        if hasCoverOfType(audio, 3, albumData['extension']):
            if flags.PIC_OVERWRITE:
                audio.clear_pictures()
                audio.add_picture(picture)
        else:
            audio.add_picture(picture)

    audio['tracktotal'] = str(albumData['totalTracks'])
    audio['disctotal'] = str(albumData['totalDisks'])
    audio['comment'] = f"Find the tracklist at {data['albumLink']}"

    if flags.YEAR and 'release_date' in data and len(data['release_date']) >= 4:
        audio['year'] = data['release_date'][0:4]

    if flags.CATALOG and 'catalog' in data and data['catalog'] != 'NA':
        audio['catalog'] = data['catalog']

    if flags.BARCODE and 'barcode' in data:
        audio['barcode'] = data['barcode']

    if flags.ORGANIZATIONS and 'organizations' in data:
        for org in data['organizations']:
            audio[org['role']] = getBest(
                org['names'], flags.languages)

    def addMultiValues(tag, tagInFile, flag=True):
        if tag in data and flag:
            temp = []
            for val in data[tag]:
                temp.append(getBest(val['names'], flags.languages))
            audio[tagInFile] = temp

    addMultiValues('lyricists', 'lyricist', flags.LYRICISTS)
    addMultiValues('performers', 'performer', flags.PERFORMERS)
    addMultiValues('arrangers', 'arranger', flags.ARRANGERS)
    addMultiValues('composers', 'composer', flags.COMPOSERS)

    # Tagging track specific details
    if flags.TITLE:
        audio['title'] = albumData['trackTitle']

    audio['discnumber'] = str(albumData['discNumber']).zfill(
        albumData['disksUpperBound'])

    audio['tracknumber'] = str(albumData['trackNumber']).zfill(
        albumData['tracksUpperBound'])
    try:
        audio.save()
        return True
    except Exception as e:
        print(e)

    return False


def tagMP3(data, albumData):
    return False
