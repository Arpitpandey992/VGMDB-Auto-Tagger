import threading
import requests
import docker
from docker.models.containers import Model
from time import sleep

from Modules.Print.utils import get_rich_console
from Modules.Utils.general_utils import get_default_logger

logger = get_default_logger(__name__, "debug")
console = get_rich_console()


class DockerClient:
    def __init__(self):
        self.client = docker.from_env()

    def pull_image(self, image_name: str):
        image_exists = any(image_name in tag for image in self.client.images.list() for tag in image.tags)
        console.log(f"pulling docker image: {image_name}")
        if not image_exists:
            self.client.images.pull(image_name)
        else:
            console.log(f"\t{image_name} already exists")

    def run_image(self, image_name: str):
        console.log(f"running docker image: {image_name}")
        is_running = any(image_name in tag for container in self.client.containers.list() for tag in container.image.tags)
        if not is_running:
            self.client.containers.run(image_name, detach=True)
        else:
            console.log(f"\t{image_name} already running")

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
            console.log(f"[green]container running @{ip_address}")
            return ip_address
        else:
            raise Exception(f"could not retrieve IP address of docker container for image: {image_name}")

    def wait_for_server_start(self, base_address: str) -> bool:
        server_ready, timed_out, stop_checking = False, False, False
        sleep_time_seconds, max_sleep_time_seconds, timeout, per_request_timeout = 1, 16, 60, 2
        default_status = "[bold green]Checking if server is ready to serve requests"
        with console.status(default_status) as status:

            def update_console_status_every_second():
                time_left_seconds = timeout
                while time_left_seconds >= 0:
                    status.update(f"{default_status},[bold magenta] Time left: {time_left_seconds} seconds")
                    sleep(1)
                    time_left_seconds -= 1
                nonlocal timed_out
                timed_out = True

            def check_if_server_ready():
                nonlocal server_ready, sleep_time_seconds, base_address, stop_checking
                while not server_ready and not stop_checking:
                    try:
                        requests.get(base_address, timeout=per_request_timeout)
                        console.log(f"[green]Server is ready to serve requests!")
                        server_ready = True
                    except requests.ConnectionError as e:
                        console.log(f"[red]Error[/] connecting to {base_address}, retrying after {sleep_time_seconds} seconds, error: {e}")
                        sleep(sleep_time_seconds)
                        sleep_time_seconds = min(sleep_time_seconds * 2, max_sleep_time_seconds)

            timeout_thread = threading.Thread(target=update_console_status_every_second)
            checker_thread = threading.Thread(target=check_if_server_ready)
            checker_thread.start()
            timeout_thread.start()
            while True:
                if not timeout_thread.is_alive() or not checker_thread.is_alive():
                    stop_checking = True
                    break
                sleep(1)
        if not server_ready:
            return False
        return True


def run_server() -> str:
    docker_client = DockerClient()
    image_name = "hufman/vgmdb:latest"
    console.log("[cyan bold]starting vgmdb.info server")
    docker_client.pull_image(image_name)
    docker_client.run_image(image_name)
    base_address = docker_client.get_server_base_address(image_name)
    successfully_started_server = docker_client.wait_for_server_start(base_address)
    if not successfully_started_server:
        console.log(f"[red bold]Could not connect to[/] {base_address}")
        raise Exception("could not connect to started docker container")
    else:
        console.log(f"[green bold]successfully started vgmdb.info server on[/] {base_address}")
    return base_address


if __name__ == "__main__":
    run_server()
