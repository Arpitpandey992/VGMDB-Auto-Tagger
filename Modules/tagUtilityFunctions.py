import requests
import io
from mutagen.flac import Picture as FLAC_PICTURE, FLAC
from mutagen.id3._frames import APIC, TALB, TDRC, TRCK, TDRL, COMM, TXXX, TPOS, TIT2
from mutagen.id3 import ID3
from PIL import Image

from Modules.flagsAndSettings import *
from Modules.utilityFunctions import getBest

# data should contain 'picture_full' and extension should be like .<ext_name> (eg: .flac, .mp3, ...)

supportedExtensions = ['.flac', '.mp3']


def hasPictureOfType(audio, pictureType, extension):
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


def deletePictureOfType(audio, pictureType, extension):
    if extension == '.flac':
        # This will remove all pictures sadly, i couldn't find any proper method to remove only one picture
        audio.clear_pictures()

    elif extension == '.mp3':
        for frame in audio.getall("APIC:"):
            if frame.type == pictureType:
                audio.pop(frame.HashKey)


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
        picture.desc = u'Cover (front)'
        data[pictureKey] = picture
        return picture

    elif extension == 'mp3':
        picture = APIC(encoding=3,
                       mime='image/jpeg',
                       type=3,
                       desc=u'Cover (front)',
                       data=image_data)
        data[pictureKey] = picture
        return picture


def tagFLAC(data, albumData):
    flags: Flags = data['flags']
    audio = FLAC(albumData['filePath'])

    # Tagging Album specific Details
    audio['album'] = albumData['albumName']
    audio['tracktotal'] = str(albumData['totalTracks'])
    audio['disctotal'] = str(albumData['totalDisks'])
    audio['comment'] = f"Find the tracklist at {data['albumLink']}"

    if flags.PICS:
        picture = getPictureObject(data, albumData['extension'])
        if picture is not None:
            if hasPictureOfType(audio, 3, albumData['extension']):
                if flags.PIC_OVERWRITE:
                    deletePictureOfType(audio, 3, albumData['extension'])
                    audio.add_picture(picture)
            else:
                audio.add_picture(picture)

    if flags.DATE and 'release_date' in data:
        audio['date'] = standardize_date(data['release_date'])

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
    flags: Flags = data['flags']
    audio = ID3(albumData['filePath'])

    audio.add(TALB(encoding=3, text=[albumData['albumName']]))
    audio.add(COMM(encoding=3, text=[f"Find the tracklist at {data['albumLink']}"]))

    if flags.PICS:
        picture = getPictureObject(data, albumData['extension'])
        if picture is not None:
            if hasPictureOfType(audio, 3, albumData['extension']):
                if flags.PIC_OVERWRITE:
                    deletePictureOfType(audio, 3, albumData['extension'])
                    audio.add(picture)
            else:
                audio.add(picture)

    if flags.DATE and 'release_date' in data:
        audio.add(TDRC(encoding=3, text=[standardize_date(data['release_date'])]))

    if flags.YEAR and 'release_date' in data and len(data['release_date']) >= 4:
        audio.add(TXXX(encoding=3, desc='Year',
                  text=[data['release_date'][0:4]]))

    if flags.CATALOG and 'catalog' in data and data['catalog'] != 'NA':
        audio.add(TXXX(encoding=3, desc='Catalog', text=[data['catalog']]))

    if flags.BARCODE and 'barcode' in data:
        audio.add(TXXX(encoding=3, desc='Barcode', text=[data['barcode']]))

    if flags.ORGANIZATIONS and 'organizations' in data:
        for org in data['organizations']:
            audio.add(TXXX(encoding=3, desc=org['role'], text=[getBest(org['names'], flags.languages)]))

    audio.add(TIT2(encoding=3, text=[albumData['trackTitle']]))

    audio.add(TRCK(
        encoding=3,
        text=[str(albumData['trackNumber']).zfill(albumData['tracksUpperBound']) +
              '/' +
              str(albumData['totalTracks'])]
    ))
    audio.add(TPOS(
        encoding=3,
        text=[str(albumData['discNumber']).zfill(albumData['disksUpperBound']) +
              '/' +
              str(albumData['totalDisks'])]
    ))

    try:
        audio.save()
        return True
    except Exception as e:
        print(e)

    return False
