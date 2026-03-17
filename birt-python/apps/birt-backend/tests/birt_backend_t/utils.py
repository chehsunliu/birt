import json
import socket
import time
from typing import IO, AnyStr


def wait_for_port(host: str, port: int):
    timeout, interval = 5.0, 0.1
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(interval)
            try:
                sock.connect((host, port))
                return
            except (socket.timeout, ConnectionRefusedError):
                time.sleep(interval)

    raise Exception(f"{host}:{port} is not available")


def read_all_logs(io: IO[AnyStr] | None) -> list[AnyStr]:
    if io is None:
        return []

    return [log for log in io.readlines()]


def read_all_json_logs(io: IO[AnyStr] | None) -> list[dict[str, AnyStr]]:
    if io is None:
        return []

    logs: list[dict[str, AnyStr]] = []
    for log in io.readlines():
        try:
            logs.append(json.loads(log))
        except json.JSONDecodeError:
            pass
    return logs
