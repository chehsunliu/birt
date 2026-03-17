import os
import subprocess
import sys
from subprocess import Popen

import httpx
import pytest

from birt_backend_t.utils import read_all_logs, wait_for_port

server_host = "127.0.0.1"
server_port = 8000
server_url = f"http://{server_host}:{server_port}"


@pytest.fixture(name="_server_daemon", autouse=True, scope="package")
def _run_server_daemon():
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "birt_backend.app:app",
            "--host",
            server_host,
            "--port",
            str(server_port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    wait_for_port(host=server_host, port=server_port)

    os.set_blocking(proc.stdout.fileno(), False)
    yield proc

    proc.terminate()
    proc.wait()


@pytest.fixture
def server_daemon(_server_daemon: Popen[str]):
    read_all_logs(_server_daemon.stdout)
    yield _server_daemon
    read_all_logs(_server_daemon.stdout)


@pytest.fixture
def client():
    with httpx.Client(base_url=server_url) as client:
        yield client
