import subprocess
import os


def run_docker_compose(compose_file_path):
    """Runs docker-compose up -d in the specified directory.

    Args:
      compose_file_path: Path to the Docker Compose file.
    """

    try:
        # Change to the directory containing the Docker Compose file
        os.chdir(compose_file_path)
        # Run the command
        subprocess.run(["docker-compose", "up", "-d"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running docker-compose: {e}")
    finally:
        # Ensure we return to the original directory
        os.chdir(os.path.abspath(os.path.dirname(__file__)))


# Example usage:
compose_file_path = "/home/arpit/Programming/Misc/vgmdb"
run_docker_compose(compose_file_path)
