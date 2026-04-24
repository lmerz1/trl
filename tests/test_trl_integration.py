from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "trl"
RUN_INTEGRATION = os.getenv("TRL_RUN_INTEGRATION") == "1"

pytestmark = pytest.mark.integration


def backend_available(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.mark.skipif(
    not RUN_INTEGRATION,
    reason="Set TRL_RUN_INTEGRATION=1 to run live backend smoke tests.",
)
def test_live_libretranslate_smoke() -> None:
    if not backend_available("127.0.0.1", 5000):
        pytest.skip("LibreTranslate is not listening on 127.0.0.1:5000")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "-p", "libretranslate", "-t", "DE", "-c", "hello"],
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip()


@pytest.mark.skipif(
    not RUN_INTEGRATION,
    reason="Set TRL_RUN_INTEGRATION=1 to run live backend smoke tests.",
)
def test_live_ollama_smoke() -> None:
    model = os.getenv("TRL_TEST_OLLAMA_MODEL")
    if not model:
        pytest.skip("Set TRL_TEST_OLLAMA_MODEL to run the live Ollama smoke test.")
    if not backend_available("127.0.0.1", 11434):
        pytest.skip("Ollama is not listening on 127.0.0.1:11434")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "-p",
            "ollama",
            "--model",
            model,
            "-t",
            "DE",
            "-c",
            "hello",
        ],
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip()
