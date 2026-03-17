from subprocess import Popen

import httpx

from birt_backend_t.utils import read_all_json_logs


def test_health(client: httpx.Client, server_daemon: Popen[str]):
    r = client.get("/api/v1/health")

    assert r.status_code == 200, r.text
    assert r.json() == {"data": {"status": "ok"}}

    logs = read_all_json_logs(server_daemon.stdout)
    assert len(logs) == 2
    assert "x_request_id" in logs[-1]
