import os
import hashlib
import getpass
import pickle
import requests
import concurrent.futures
from typing import Any
from bs4 import BeautifulSoup, Tag

# remove
import sys

sys.path.append(os.getcwd())
# remove

from Imports.constants import THREAD_EXECUTOR_NUM_THREADS
from Modules.Print.utils import get_rich_console
from Modules.Utils.general_utils import getSha256
from Modules.Utils.network_utils import download_file

session = requests.Session()


def Soup(data: Any):
    return BeautifulSoup(data, "html.parser")


def is_logged_in(current_session: Any) -> bool:
    x = current_session.get("https://vgmdb.net/forums/private.php")
    soup = Soup(x.content)
    login_element = soup.find("a", href="#", string="Login")
    return login_element is None


def login(config: str):
    global session
    logged_in = False
    if os.path.isfile(config):
        temp_session = pickle.load(open(config, "rb"))
        if is_logged_in(temp_session):
            logged_in = True
            session = temp_session
    if not logged_in:
        print("Please log in to VGMDB for downloading all scans")
        while True:
            username = input("VGMdb username:\t")
            password = getpass.getpass("VGMdb password:\t")
            base_url = "https://vgmdb.net/forums/"
            x = session.post(
                base_url + "login.php?do=login",
                {
                    "vb_login_username": username,
                    "vb_login_password": password,
                    "vb_login_md5password": hashlib.md5(password.encode()).hexdigest(),
                    "vb_login_md5password_utf": hashlib.md5(password.encode()).hexdigest(),
                    "cookieuser": 1,
                    "do": "login",
                    "s": "",
                    "securitytoken": "guest",
                },
            )
            table = Soup(x.content).find("table", class_="tborder", width="70%")
            panel = table.find("div", class_="panel")  # type: ignore
            message = panel.text.strip()  # type: ignore
            print(message)

            if message.startswith("You"):
                if message[223] == "5":
                    raise SystemExit(1)
                print(message)
                continue
            elif message.startswith("Wrong"):
                raise SystemExit(1)
            else:
                break


def remove(instring: str, chars: str):
    for i in range(len(chars)):
        instring = instring.replace(chars[i], "")
    return instring


def ensure_dir(f: str):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def downloadScans(outputDir: str, albumID: str):
    console = get_rich_console()
    cwd = os.path.abspath(__file__)
    scriptdir = os.path.dirname(cwd)
    config = os.path.join(scriptdir, "vgmdbrip.pkl")
    login(config)
    with console.status("[bold magenta]Authenticating and Fetching Scans") as status:
        soup = Soup(session.get("https://vgmdb.net/album/" + albumID).content)
        gallery = soup.find("div", attrs={"class": "covertab", "id": "cover_gallery"})

        if not isinstance(gallery, Tag):
            return

        scans = gallery.find_all("a", attrs={"class": "highslide"})
        pictureCount = len(scans)

        finalScanFolder = os.path.join(outputDir, "Scans") if pictureCount > 1 else outputDir
        if not os.path.exists(finalScanFolder):
            os.makedirs(finalScanFolder)

        def download_scan(scan: Any):
            url = scan["href"]
            title = remove(scan.text.strip(), r'"*/:<>?\|')
            try:
                download_file(url=url, output_dir=finalScanFolder, name=title)
                console.log(f"[green]Downloaded:[/green] [magenta bold]{title}")
            except FileExistsError:
                console.log(f"[yellow]Already Exists:[/yellow] [cyan bold]{title}")
            except Exception as e:
                console.log(f"[red]Error while downloading: {e}")

        numThreads = THREAD_EXECUTOR_NUM_THREADS
        status.update(f"[bold magenta]Downloading Scans with {numThreads} Threads")
        with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
            tasks = [executor.submit(download_scan, scan) for scan in scans]

        concurrent.futures.wait(tasks)

    removeOldDuplicateScans(finalScanFolder)
    pickle.dump(session, open(config, "wb"))


def removeOldDuplicateScans(scanFolder: str):
    console = get_rich_console()
    files = [os.path.join(scanFolder, file) for file in os.listdir(scanFolder) if os.path.isfile(os.path.join(scanFolder, file))]
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
    hashes_found: set[str] = set()
    filesToRemove: list[str] = []
    for filePath in sorted_files:
        sha256 = getSha256(filePath)
        if sha256 not in hashes_found:
            hashes_found.add(sha256)
        else:
            filesToRemove.append(filePath)

    for filePath in sorted(filesToRemove):
        os.remove(filePath)
        console.log(f"removing {os.path.basename(filePath)} as it is a duplicate")


if __name__ == "__main__":
    import shutil

    folder = f"{os.path.expanduser('~')}/Downloads/test"
    shutil.rmtree(folder, ignore_errors=True)
    downloadScans(folder, "87406")
