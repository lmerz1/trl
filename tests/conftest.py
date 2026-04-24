from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from threading import Thread
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class TestServer:
    def __init__(self, response_body: dict[str, Any], status_code: int = 200):
        self.response_body = response_body
        self.status_code = status_code
        self.requests: list[dict[str, Any]] = []
        self.server = self._build_server()
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    def _build_server(self) -> ThreadingHTTPServer:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                content_length = int(self.headers.get("Content-Length", "0"))
                raw_body = self.rfile.read(content_length).decode("utf-8")
                payload: Any = raw_body
                content_type = self.headers.get("Content-Type", "")

                if "application/json" in content_type and raw_body:
                    payload = json.loads(raw_body)

                outer.requests.append(
                    {
                        "path": self.path,
                        "headers": dict(self.headers),
                        "body": payload,
                    }
                )
                body = json.dumps(outer.response_body).encode("utf-8")
                self.send_response(outer.status_code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        return ThreadingHTTPServer(("127.0.0.1", 0), Handler)

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def start(self) -> "TestServer":
        self.thread.start()
        return self

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


@pytest.fixture
def json_server() -> Any:
    servers: list[TestServer] = []

    def factory(response_body: dict[str, Any], status_code: int = 200) -> TestServer:
        server = TestServer(response_body, status_code).start()
        servers.append(server)
        return server

    yield factory

    for server in servers:
        server.stop()
