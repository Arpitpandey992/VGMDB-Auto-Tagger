import requests
import docker
from docker.models.containers import Model
from time import sleep

from Modules.Utils.general_utils import get_default_logger

logger = get_default_logger(__name__, "debug")


class DockerClient:
    def __init__(self):
        self.client = docker.from_env()

    def pull_image(self, image_name: str):
        image_exists = any(image_name in tag for image in self.client.images.list() for tag in image.tags)
        logger.debug(f"pulling docker image: {image_name}")
        if not image_exists:
            self.client.images.pull(image_name)
        else:
            logger.debug(f"{image_name} already exists")

    def run_image(self, image_name: str):
        logger.debug(f"running docker image: {image_name}")
        is_running = any(image_name in tag for container in self.client.containers.list() for tag in container.image.tags)
        if not is_running:
            self.client.containers.run(image_name, detach=True)
        else:
            logger.debug(f"{image_name} already running")

    def get_running_container(self, image_name: str) -> Model | None:
        matching_containers = [container for container in self.client.containers.list() if any(image_name in tag for tag in container.image.tags)]
        if matching_containers:
            return matching_containers[0]
        else:
            return None

    def get_server_base_address(self, image_name: str) -> str:
        container = self.get_running_container(image_name)
        if not container:
            raise Exception("container not running")
        container_info = container.attrs
        if container_info:
            ip_address = f"http://{container_info['NetworkSettings']['IPAddress']}"
            logger.debug(f"container running @{ip_address}")
            return ip_address
        else:
            raise Exception(f"could not retrieve IP address of docker container for image: {image_name}")

    def wait_for_server_start(self, base_address: str):
        server_ready = False
        sleep_time_seconds, max_sleep_time_seconds = 1, 30
        logger.debug("checking if server is ready to serve requests")
        while not server_ready:
            try:
                requests.get(base_address)
                logger.debug("server is ready to serve requests!")
                server_ready = True
            except requests.ConnectionError as e:
                logger.debug(f"error connecting to {base_address}, retrying after {sleep_time_seconds} seconds, error: {e}")
                sleep(sleep_time_seconds)
                sleep_time_seconds = min(sleep_time_seconds * 2, max_sleep_time_seconds)


def run_server() -> str:
    docker_client = DockerClient()
    image_name = "hufman/vgmdb:latest"
    logger.debug("starting vgmdb.info server")
    docker_client.pull_image(image_name)
    docker_client.run_image(image_name)
    base_address = docker_client.get_server_base_address(image_name)
    docker_client.wait_for_server_start(base_address)
    logger.debug(f"successfully started vgmdb.info server on {base_address}")
    return base_address


if __name__ == "__main__":
    run_server()
