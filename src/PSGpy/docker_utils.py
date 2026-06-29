# *******************************************************
# Lorenzo Buriola - University of Bologna - CNR-ISAC
# PSGpy - docker_utils.py
# Functions that make use of the docker SDK for pyhton
# to manage docker containers from within python apps
# *******************************************************

import docker
import os
from docker.errors import NotFound, APIError
from pathlib import Path

def is_container_running(name):
    """
    Check if a Docker container is running
    
    Parameters
    ----------
    name: string - name of the container
    url: string - url of the container
    """
    socket = get_docker_socket()
    docker_client = docker.DockerClient(base_url=socket)
    try:
        container = docker_client.containers.get(name)
    except NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    except APIError as exc:
        print(f"API error occurred: {exc.explanation}")
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == "running"

def start_container(name, url) -> None:
    """
    Start a Docker container
    
    Parameters
    ----------
    name: string - name of the container
    url: string - url of the container
    """
    docker_client = docker.DockerClient(base_url=url)
    docker_client.containers.get(name).start()

def stop_container(name, url) -> None:
    """
    Stop a Docker container
    
    Parameters
    ----------
    name: string - name of the container
    url: string - url of the container
    """
    docker_client = docker.DockerClient(base_url=url)
    docker_client.containers.get(name).stop()

def get_docker_socket():
    candidates = [
        os.environ.get("DOCKER_HOST"),  # best case
        f"unix:///run/user/{os.getuid()}/docker.sock",
        "unix:///var/run/docker.sock",
    ]

    for sock in candidates:
        if not sock:
            continue
        path = sock.replace("unix://", "")
        if Path(path).exists():
            return sock
    raise RuntimeError("Docker socket not found")