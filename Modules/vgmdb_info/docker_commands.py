from email.mime import base
from typing import Optional
import requests
import docker
from docker.models.containers import Model
from time import sleep

from Utility.generalUtils import get_default_logger

logger = get_default_logger(__name__, 'info')
client = docker.from_env()


def pull_image(image_name: str):
    image_exists = any(image_name in tag for image in client.images.list() for tag in image.tags)
    logger.debug(f"pulling docker image: {image_name}")
    if not image_exists:
        client.images.pull(image_name)
    else:
        logger.debug(f"{image_name} already exists")


def run_image(image_name: str):
    logger.debug(f"running docker image: {image_name}")
    is_running = any(image_name in tag for container in client.containers.list() for tag in container.image.tags)
    if not is_running:
        client.containers.run(image_name, detach=True)
    else:
        logger.debug(f"{image_name} already running")


def get_running_container(image_name: str) -> Optional[Model]:
    matching_containers = [container for container in client.containers.list() if any(image_name in tag for tag in container.image.tags)]
    if matching_containers:
        return matching_containers[0]
    else:
        return None


def get_server_base_address(image_name: str) -> str:
    container = get_running_container(image_name)
    if not container:
        raise Exception('container not running')
    container_info = container.attrs
    if container_info:
        ip_address = f"http://{container_info['NetworkSettings']['IPAddress']}"
        logger.debug(f'container running @{ip_address}')
        return ip_address
    else:
        raise Exception(f'could not retrieve IP address of docker container for image: {image_name}')


def wait_for_server_start(base_address: str):
    server_ready = False
    sleep_time_seconds, max_sleep_time_seconds = 1, 30
    while not server_ready:
        try:
            requests.get(base_address)
            server_ready = True
        except requests.ConnectionError:
            sleep(sleep_time_seconds)
            sleep_time_seconds = min(sleep_time_seconds * 2, max_sleep_time_seconds)


def run_server() -> str:
    image_name = 'hufman/vgmdb:latest'
    pull_image(image_name)
    run_image(image_name)
    base_address = get_server_base_address(image_name)
    wait_for_server_start(base_address)
    return base_address


if __name__ == '__main__':
    base_address = run_server()
    wait_for_server_start(base_address)
    print(f"vgmdb.info running on {base_address}")
