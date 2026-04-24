from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "trl"


def run_cli(
    *args: str, input_text: str | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    for key in (
        "TRL_API_KEY",
        "TRL_DEFAULT_PROVIDER",
        "TRL_DEFAULT_TARGET_LANG",
        "TRL_OLLAMA_MODEL",
    ):
        merged_env.pop(key, None)
    if env:
        merged_env.update(env)

    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=input_text,
        text=True,
        capture_output=True,
        env=merged_env,
        cwd=ROOT,
        check=False,
    )


def test_cli_translates_inline_content_with_fake_libretranslate(json_server) -> None:
    server = json_server(
        {
            "translatedText": "Bonjour",
            "detectedLanguage": {"language": "en"},
        }
    )

    result = run_cli(
        "-p",
        "libretranslate",
        "--base-url",
        server.base_url,
        "-t",
        "FR",
        "-c",
        "Hello",
    )

    assert result.returncode == 0
    assert result.stdout == "Bonjour\n"
    assert result.stderr == ""
    assert server.requests[0]["path"] == "/translate"
    assert server.requests[0]["body"] == {
        "q": "Hello",
        "source": "auto",
        "target": "FR",
        "format": "text",
    }


def test_cli_reads_stdin_with_fake_libretranslate(json_server) -> None:
    server = json_server(
        {
            "translatedText": "Guten Tag",
            "detectedLanguage": {"language": "en"},
        }
    )

    result = run_cli(
        "-p",
        "libretranslate",
        "--base-url",
        server.base_url,
        "-t",
        "DE",
        input_text="Hello there",
    )

    assert result.returncode == 0
    assert result.stdout == "Guten Tag\n"
    assert server.requests[0]["body"]["q"] == "Hello there"


def test_cli_reads_input_file_with_fake_libretranslate(
    json_server, tmp_path: Path
) -> None:
    path = tmp_path / "input.txt"
    path.write_text("Good night", encoding="utf-8")
    server = json_server(
        {
            "translatedText": "Buenas noches",
            "detectedLanguage": {"language": "en"},
        }
    )

    result = run_cli(
        "-p",
        "libretranslate",
        "--base-url",
        server.base_url,
        "-t",
        "ES",
        "-i",
        str(path),
    )

    assert result.returncode == 0
    assert result.stdout == "Buenas noches\n"
    assert server.requests[0]["body"]["q"] == "Good night"


def test_cli_rejects_unknown_provider() -> None:
    result = run_cli("-p", "unknown", "-t", "FR", "-c", "Hello")

    assert result.returncode == 1
    assert "Unknown provider" in result.stderr


def test_cli_requires_ollama_model() -> None:
    result = run_cli("-p", "ollama", "-t", "FR", "-c", "Hello")

    assert result.returncode == 1
    assert "no model specified for Ollama" in result.stderr
