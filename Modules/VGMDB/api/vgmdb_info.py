import os
import subprocess
import threading
import git
import requests
import docker
from time import sleep

from docker.models.resource import Model

# REMOVE
import sys

sys.path.append(os.getcwd())
# REMOVE

from Modules.Print.utils import get_rich_console
from Modules.Utils.general_utils import get_default_logger
from Modules.VGMDB import constants

logger = get_default_logger(__name__, "debug")
console = get_rich_console()


def wait_for_server_start(base_address: str) -> bool:
    console.log(f"[bold]testing {base_address}")
    server_ready, timed_out, stop_checking = False, False, False
    sleep_time_seconds, max_sleep_time_seconds, timeout, per_request_timeout = 1, 16, 60, 2
    default_status = "[bold]checking if server is ready to serve requests"
    with console.status(default_status) as status:

        def update_console_status_every_second():
            nonlocal server_ready
            time_left_seconds = timeout
            while not server_ready and time_left_seconds >= 0:
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
                    console.log(f"[green]{base_address} is ready to serve requests!")
                    server_ready = True
                except requests.ConnectionError as e:
                    console.log(f"[red]error[/] connecting to {base_address}, retrying after {sleep_time_seconds} seconds, error: {e}")
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


def run_server_using_docker() -> str:
    docker_client = DockerClient()
    image_name = "hufman/vgmdb:latest"
    console.log(f"[cyan bold]starting vgmdb.info server by running docker run {image_name}")
    docker_client.pull_image(image_name)
    docker_client.run_image(image_name)
    return docker_client.get_server_base_address(image_name)


def run_server_using_docker_compose() -> str:
    console.log("[magenta bold]starting vgmdb.info server using docker compose")
    vgmdb_info_git_url: str = "https://github.com/Arpitpandey992/vgmdb.git"
    current_file_path: str = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    repo_clone_path: str = os.path.join(current_file_path, "vgmdb")

    def clone_or_pull_repo(repo_url: str, clone_path: str):
        try:
            if os.path.exists(clone_path):
                console.log(f"[yellow]pulling latest changes in {repo_url}")
                try:
                    repo = git.Repo(clone_path)
                    fetch_info_list = repo.remotes.origin.pull()
                    for fetch_info in fetch_info_list:
                        if fetch_info.flags & git.FetchInfo.NEW_HEAD:
                            console.log(f"New branch '{fetch_info.ref.name}' with commit {fetch_info.commit.hexsha}")
                        elif fetch_info.flags & git.FetchInfo.FORCED_UPDATE:
                            console.log(f"Branch '{fetch_info.ref.name}' was force-updated to commit {fetch_info.commit.hexsha}")
                        else:
                            console.log(f"Updated branch '{fetch_info.ref.name}' to commit {fetch_info.commit.hexsha}")
                    console.log(f"[green]Pulled latest changes in {clone_path}")
                except git.GitCommandError as e:
                    message = f"Error pulling latest changes: {e}"
                    console.log(f"[red]{message}")
                    raise Exception(message)
            else:
                console.log(f"[yellow]cloning {repo_url} to {clone_path}")
                try:
                    repo = git.Repo.clone_from(repo_url, clone_path)
                    console.log(f"[green]Cloned repository to {clone_path}")
                except git.GitCommandError as e:
                    message = f"Error cloning repository: {e}"
                    console.log(f"[red]{message}")
        except Exception as e:
            message = f"Unexpected error: {e}"
            console.log(f"[red]{message}")

    def run_docker_compose(source_dir: str):
        console.log(f"[yellow]running docker compose up -d in {source_dir}")
        original_working_directory: str = os.getcwd()
        try:
            os.chdir(source_dir)
            result = subprocess.run(["docker-compose", "up", "-d"], check=True)

            if result.returncode == 0:
                console.log(f"successfully started vgmdb.info using docker compose")
            else:
                message = f"error running Docker Compose to run vgmdb.info server, error: {result.stderr}"
                console.log(f"[red bold]{message}")
                raise Exception(message)
        except Exception as e:
            message = f"docker-compose command not found. Please make sure Docker Compose is installed and available in your PATH. error: {e}"
            console.log(f"[red bold]{message}")
            raise Exception(message)
        finally:
            os.chdir(original_working_directory)

    clone_or_pull_repo(vgmdb_info_git_url, repo_clone_path)
    run_docker_compose(repo_clone_path)

    return constants.VGMDB_INFO_DOCKER_COMPOSER_BASE_URL


def run_vgmdb_info_server() -> str:
    if constants.VGMDB_INFO_LOCAL_RUN_TYPE == "docker-compose":
        server_base_url = run_server_using_docker_compose()
    else:
        server_base_url = run_server_using_docker()

    successfully_started_server = wait_for_server_start(server_base_url)
    if not successfully_started_server:
        console.log(f"[red bold]Could not connect to[/] {server_base_url}")
        raise Exception("could not connect to started docker container")
    else:
        console.log(f"[green bold]successfully started vgmdb.info server on[/] {server_base_url}")
    return server_base_url


if __name__ == "__main__":
    run_vgmdb_info_server()
