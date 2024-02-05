import os
import requests
from urllib.parse import urlparse
import urllib.request


def get_raw_data_from_url(url: str) -> bytes:
    """
    fetches and returns the raw data present inside url

    Args:
        url (str): url of the file to be downloaded
    Returns:
        bytes: raw data received from the url
    """
    response = requests.get(url)
    return response.content


def download_file(url: str, output_dir: str, name: str | None = None) -> str:
    """
    downloads a file to local file system which is directly accessible online

    Args:
        url (str): url of the file to be downloaded
        output_dir (str): output directory where the file is to be downloaded
        name: (Optional[str]): manual name of the file without extension. if not provided, name will be automatically decided
    Returns:
        str: path of the downloaded file
    """
    """
    downloads a file to local file system which is directly accessible online

    Args:
        url (str): url of the file to be downloaded
        path (str): folder path where the file is to be downloaded
        name: (Optional[str]): manual name of the file without extension. if not provided, name will be automatically decided
    Returns:
        str: path of the downloaded file
    """
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"download folder: {output_dir} does not exist")
    parsedUrl = urlparse(url)
    fileName = os.path.basename(parsedUrl.path)
    _, extension = os.path.splitext(fileName)
    fileName = name + extension if name else fileName
    filePath = os.path.join(output_dir, fileName)

    if os.path.exists(filePath):
        raise FileExistsError(f"file already exists: {fileName}")  # logging fileName in error instead of filePath to reduce clutter in Console

    urllib.request.urlretrieve(url, filePath)
    return filePath


if __name__ == "__main__":
    print(
        download_file(
            "https://i0.wp.com/www.alphr.com/wp-content/uploads/2021/04/Screenshot_9-26.png?extra=3",
            "/Users/arpit/Downloads",
            "launch_2",
        )
    )
