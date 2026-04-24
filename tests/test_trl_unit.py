from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
import requests

import trl


class FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


@pytest.mark.parametrize(
    ("provider_name", "provider_type"),
    [
        ("deepl", trl.DeepLProvider),
        ("d", trl.DeepLProvider),
        ("libretranslate", trl.LibreTranslateSelfhostedProvider),
        ("lt", trl.LibreTranslateSelfhostedProvider),
        ("ollama", trl.OllamaProvider),
        ("o", trl.OllamaProvider),
    ],
)
def test_get_provider_aliases(
    provider_name: str, provider_type: type[trl.BaseTranslationProvider]
) -> None:
    provider = trl.get_provider(provider_name, "key")
    assert isinstance(provider, provider_type)


def test_resolve_base_url_warns_when_port_is_ignored() -> None:
    with pytest.warns(UserWarning, match="Port argument is ignored"):
        base_url = trl.BaseTranslationProvider.resolve_base_url(
            "ollama", default_port=11434, port=9999, base_url="http://example.test/"
        )

    assert base_url == "http://example.test"


def test_build_url_normalizes_slashes() -> None:
    assert (
        trl.BaseTranslationProvider.build_url("http://localhost:1234/", "translate")
        == "http://localhost:1234/translate"
    )


def test_read_content_source_prefers_direct_content() -> None:
    assert trl.read_content_source("hello", None, False) == "hello"


def test_read_content_source_reads_file(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("hello from file", encoding="utf-8")

    assert trl.read_content_source(None, str(path), False) == "hello from file"


def test_read_content_source_reads_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(trl.sys, "stdin", StringIO("hello from stdin"))

    assert trl.read_content_source(None, "-", False) == "hello from stdin"


def test_get_editor_command_uses_visual_and_adds_wait(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VISUAL", "code")

    assert trl.get_editor_command() == ["code", "--wait"]


def test_add_editor_wait_args_does_not_duplicate_wait_flag() -> None:
    assert trl.add_editor_wait_args(["code", "--wait"]) == ["code", "--wait"]


def test_load_api_key_prefers_direct_key(tmp_path: Path) -> None:
    path = tmp_path / "api-key.txt"
    path.write_text("TRL_API_KEY file-key\n", encoding="utf-8")

    assert trl.load_api_key(path, "direct-key", "env-key") == "direct-key"


def test_deepl_translate_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict] = []

    def fake_post(
        url: str, headers: dict | None = None, data: dict | None = None
    ) -> FakeResponse:
        calls.append({"url": url, "headers": headers, "data": data})
        return FakeResponse(
            200,
            {
                "translations": [
                    {"text": "Bonjour", "detected_source_language": "EN"}
                ]
            },
        )

    monkeypatch.setattr(trl.requests, "post", fake_post)

    translated = trl.DeepLProvider("secret").translate("FR", "Hello")

    assert translated == "Bonjour"
    assert calls == [
        {
            "url": "https://api-free.deepl.com/v2/translate",
            "headers": {"Authorization": "DeepL-Auth-Key secret"},
            "data": {"text": "Hello", "target_lang": "FR"},
        }
    ]


def test_libretranslate_translate_success_more_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict] = []

    def fake_post(
        url: str, json: dict | None = None, headers: dict | None = None
    ) -> FakeResponse:
        calls.append({"url": url, "json": json, "headers": headers})
        return FakeResponse(
            200,
            {
                "translatedText": "Hallo",
                "detectedLanguage": {"language": "en"},
            },
        )

    monkeypatch.setattr(trl.requests, "post", fake_post)

    translated = trl.LibreTranslateSelfhostedProvider("").translate(
        "DE", "Hello", more_output=True, base_url="http://127.0.0.1:5000"
    )

    assert "Detected source language: EN" in translated
    assert ">>> 'Hallo'" in translated
    assert calls[0]["url"] == "http://127.0.0.1:5000/translate"
    assert calls[0]["json"] == {
        "q": "Hello",
        "source": "auto",
        "target": "DE",
        "format": "text",
    }


def test_ollama_translate_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict] = []

    def fake_post(url: str, json: dict | None = None) -> FakeResponse:
        calls.append({"url": url, "json": json})
        return FakeResponse(200, {"response": "Bonjour"})

    monkeypatch.setattr(trl.requests, "post", fake_post)

    translated = trl.OllamaProvider("").translate(
        "FR",
        "Hello",
        source_lang="EN",
        base_url="http://127.0.0.1:11434",
        model="test-model",
    )

    assert translated == "Bonjour"
    assert calls[0]["url"] == "http://127.0.0.1:11434/api/generate"
    assert calls[0]["json"]["model"] == "test-model"
    assert calls[0]["json"]["options"] == {"temperature": 0}
    assert "The source language is EN" in calls[0]["json"]["system"]


def test_provider_request_errors_are_wrapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(*args: object, **kwargs: object) -> FakeResponse:
        raise requests.RequestException("boom")

    monkeypatch.setattr(trl.requests, "post", fake_post)

    with pytest.raises(RuntimeError, match="failed to reach DeepL"):
        trl.DeepLProvider("secret").translate("FR", "Hello")


def test_main_rejects_missing_api_key(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TRL_API_KEY", raising=False)
    monkeypatch.delenv("TRL_DEFAULT_TARGET_LANG", raising=False)

    exit_code = trl.main(["-p", "deepl", "-t", "FR", "-c", "Hello"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Please provide a valid API key" in captured.err


def test_main_rejects_missing_content(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TRL_API_KEY", "secret")
    monkeypatch.setattr(trl.sys.stdin, "isatty", lambda: True)

    exit_code = trl.main(["-p", "deepl", "-t", "FR"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Content is required" in captured.err
