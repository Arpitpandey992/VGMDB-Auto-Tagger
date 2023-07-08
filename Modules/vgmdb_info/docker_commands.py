from typing import Optional
import docker
from docker.models.containers import Container
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


def get_running_container(image_name: str) -> Optional[Container]:
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


def run_server() -> str:
    image_name = 'hufman/vgmdb:latest'
    pull_image(image_name)
    run_image(image_name)
    base_address = get_server_base_address(image_name)
    return base_address


if __name__ == '__main__':
    run_server()
