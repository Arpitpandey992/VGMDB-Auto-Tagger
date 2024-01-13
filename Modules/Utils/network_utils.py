import os
import requests
from urllib.parse import urlparse
import urllib.request


def getRawDataFromUrl(url: str) -> bytes:
    """
    fetches and returns the raw data present inside url

    Args:
        url (str): url of the file to be downloaded
    Returns:
        bytes: raw data received from the url
    """
    response = requests.get(url)
    return response.content


def downloadFile(url: str, output_dir: str, name: str | None = None) -> str:
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
    imageName = os.path.basename(parsedUrl.path)
    _, extension = os.path.splitext(imageName)
    imageName = name + extension if name else imageName
    imagePath = os.path.join(output_dir, imageName)

    if os.path.exists(imagePath):
        raise FileExistsError(f"file already exists: {imagePath}")

    urllib.request.urlretrieve(url, imagePath)
    return imagePath


if __name__ == "__main__":
    print(
        downloadFile(
            "https://i0.wp.com/www.alphr.com/wp-content/uploads/2021/04/Screenshot_9-26.png?extra=3",
            "/Users/arpit/Downloads",
            "launch_2",
        )
    )
