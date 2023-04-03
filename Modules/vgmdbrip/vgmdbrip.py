from sys import argv
import os
import json
import hashlib
import getpass
import pickle
import requests
from bs4 import BeautifulSoup
from Types.albumData import AlbumData
from Types.otherData import OtherData
from Utility.generalUtils import downloadPicture
session = requests.Session()


def Soup(data):
    return BeautifulSoup(data, "html.parser")


def login(config):
    global session
    if os.path.isfile(config):
        session = pickle.load(open(config, "rb"))
    else:
        while True:
            username = input('VGMdb username:\t')
            password = getpass.getpass('VGMdb password:\t')
            base_url = 'https://vgmdb.net/forums/'
            x = session.post(base_url + 'login.php?do=login', {
                'vb_login_username': username,
                'vb_login_password': password,
                'vb_login_md5password': hashlib.md5(password.encode()).hexdigest(),
                'vb_login_md5password_utf': hashlib.md5(password.encode()).hexdigest(),
                'cookieuser': 1,
                'do': 'login',
                's': '',
                'securitytoken': 'guest'
            })
            table = Soup(x.content).find(
                'table', class_='tborder', width="70%")
            panel = table.find('div', class_='panel')  # type: ignore
            message = panel.text.strip()  # type: ignore
            print(message)

            if message.startswith('You'):
                if message[223] == '5':
                    raise SystemExit(1)
                print(message)
                continue
            elif message.startswith('Wrong'):
                raise SystemExit(1)
            else:
                break


def remove(instring, chars):
    for i in range(len(chars)):
        instring = instring.replace(chars[i], "")
    return instring


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def getPictures(folder: str, albumID: str):
    cwd = os.path.abspath(__file__)
    scriptdir = os.path.dirname(cwd)
    config = os.path.join(scriptdir, 'vgmdbrip.pkl')
    login(config)
    soup = Soup(session.get("https://vgmdb.net/album/" + albumID).content)
    gallery = soup.find("div", attrs={"class": "covertab",
                                      "id": "cover_gallery"})

    scans = gallery.find_all("a", attrs={"class": "highslide"})  # type:ignore
    pictureCount = len(scans)

    finalScanFolder = os.path.join(folder, 'Scans') if pictureCount > 1 else folder
    if not os.path.exists(finalScanFolder):
        os.makedirs(finalScanFolder)

    for scan in scans:
        url = scan["href"]
        title = remove(scan.text.strip(), "\"*/:<>?\|")  # type: ignore
        downloadPicture(URL=url, path=finalScanFolder, name=title)
    pickle.dump(session, open(config, "wb"))


def getPicturesTheOldWay(albumData: AlbumData, otherData: OtherData):
    frontPictureExists = False
    coverPath = os.path.join(otherData['folder_path'], 'Scans')
    if not os.path.exists(coverPath):
        os.makedirs(coverPath)
    for cover in albumData.get('covers', []):
        downloadPicture(URL=cover['full'], path=coverPath, name=cover['name'])
        if cover['name'].lower() == 'front' or cover['name'].lower == 'cover':
            frontPictureExists = True
    if not frontPictureExists and 'picture_full' in albumData:
        downloadPicture(URL=albumData['picture_full'],
                        path=coverPath, name='Front')
