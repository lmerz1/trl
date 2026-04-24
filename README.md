
# trl

`trl` is a small Unix-friendly command-line translator. It wraps a few
translation providers behind one CLI and reads text from flags, files, stdin,
or a local editor.

The default provider is DeepL, which at the time of writing is free up to
500,000 monthly characters translated.
Self-hosted providers such as LibreTranslate and Ollama are also supported.


## Requirements

- A Unix-like shell environment
- Python 3.9 or newer
- The Python package `requests`


## Getting started

Download the standalone script somewhere on your `PATH`:

```sh
mkdir -p ~/.local/bin  # and append the directory to your $PATH
curl -fsSL https://raw.githubusercontent.com/lmerz1/trl/main/trl -o ~/.local/bin/trl
chmod +x ~/.local/bin/trl
```

### Recommended: run it with `uv`

If you already use [`uv`](https://docs.astral.sh/uv/), this is the least
surprising way to satisfy the `requests` dependency for a single-file script
without touching your system Python:

```sh
uv run --with requests ~/.local/bin/trl -h
```

If you want to invoke `trl` this way regularly, add a shell alias:

```sh
alias trl='uv run --quiet --with requests ~/.local/bin/trl'
```

### Alternative: install `requests` into your active Python

If you prefer to run the script directly through its shebang, install
`requests` for the same `python3` that `/usr/bin/env python3` will resolve to:

```sh
python3 -m pip install --user requests
trl -h
```

### Alternative: use a dedicated virtual environment

If you want a persistent isolated environment without using `uv run` on every
invocation:

```sh
uv venv ~/.local/share/trl-venv
~/.local/share/trl-venv/bin/python -m pip install requests
~/.local/share/trl-venv/bin/python ~/.local/bin/trl -h
```


## Quick start

### DeepL (default provider)

DeepL is the default backend. It requires an API key.

Create a free API key with [DeepL](https://www.deepl.com/en/pro-api?cta=header-pro-api/)
and export it:

```sh
export TRL_API_KEY='your-api-key-here'
```

Then run:

```sh
trl -t ES -c "Hallo Welt! Wie geht's?"
```

### Ollama

Ollama does not require an API key, but it does require a model name and a
reachable Ollama server:

```sh
trl --provider ollama --model qwen3.5:4b -t DE -c "Please translate this."
```

### LibreTranslate

A self-hosted LibreTranslate instance usually does not require an API key. By
default `trl` expects it on `http://localhost:5000`:

```sh
trl -p libretranslate -t FR -c "Hello world"
```


## Providers

These are the provider values currently accepted by `--provider`/`-p`:

| Provider value   | Aliases for convenience      | Backend                    | API key      | Default connection       |
| ---              | ---                          | ---                        | ---          | ---                      |
| `deepl`          | `d`                          | DeepL Free API             | Required     | DeepL-hosted API         |
| `libretranslate` | `local_libre`, `libre`, `lt` | Self-hosted LibreTranslate | Optional*    | `http://localhost:5000`  |
| `ollama`         | `local_ollama`, `o`          | Ollama HTTP API            | Not required | `http://localhost:11434` |

*Depending on how your instance is set up


Notes:

- `--model` is required for `ollama` unless `TRL_OLLAMA_MODEL` is set.
- `--port` and `--base-url` may matter for self-hosted providers.
  If both are set, `--base-url` wins.
- When using DeepL, `--port`, `--base-url`, and `--model` are ignored.


## Configuration

### Environment variables

All environment variables are **optional**:
`trl` will work even when none are set, however in this case, you may have to
use the corresponding option if a required argument is missing.

- `TRL_API_KEY`: API key for DeepL, or optionally for a LibreTranslate instance
  that requires one
- `TRL_DEFAULT_TARGET_LANG`: default target language, so you can omit `-t`
- `TRL_OLLAMA_MODEL`: default model for the `ollama` provider

Examples:

```sh
export TRL_API_KEY="your-api-key-here"
export TRL_DEFAULT_TARGET_LANG="en"
export TRL_OLLAMA_MODEL="translategemma:4b"
```

If you rotate between multiple keys, keep them in separate shell variables and
assign the active one only when needed:

```sh
export DEEPL_API_KEY_1="your-api-key-here:fx"
TRL_API_KEY="$DEEPL_API_KEY_1" trl -t EN -c "test"
```

### API key file

You may also store a key in a text file and pass it via `-f` / `--file`.

The file should contain a line like:

```text
TRL_API_KEY your-api-key-here
```

Then invoke:

```sh
trl -f /path/to/API_KEYS.txt -t EN -c "test"
```

Authentication precedence is:

1. `--key`
2. `--file`
3. `TRL_API_KEY`


## Input modes

You can provide content in any one of these ways:

- `-c`, `--content`: text directly on the command line
- `-i`, `--input-file`: read from a file
- `-i -`: read from stdin explicitly
- `--edit`: compose text in a local editor
- stdin without `-i -`: `trl` will also read piped input automatically

`--edit` is Unix-only. `trl` checks `VISUAL` and `EDITOR` first, then falls
back to common editors such as `nano`, `vim`, `hx`, `code`, `codium`,
`cursor`, and `zed`.


## Common usage

```sh
trl -h
trl -t ES -c "Hallo Welt! Wie geht's?"
trl -c "What does Hungarian look like again..." -t HU
echo "hello world" | trl -t FR
trl -t EN < query.txt > output.txt
trl -t EN --input-file query.txt > output.txt
trl -t EN --input-file -
trl -t EN --edit
trl -p ollama --model qwen3.5:4b -t DE -c "Please translate this."
trl -p ollama --base-url https://remote-host.example:11434 --model translategemma:4b -t FR -c "Remote inference works too."
trl -t JA <<'EOF'
Can my terminal display "special" shell characters like `'"!? safely?
EOF
```

Example output:

```text
$ trl -c "Can my terminal display a Japanese script?" -t JA
端末に日本語を表示できますか？
```

With `-m` / `--more-output`:

```text
$ trl -c "What does Hungarian look like again? I forgot..." -t HU -m

    Request:
    Target language: HU
    >>> 'What does Hungarian look like again? I forgot...'

    Answer:
    Detected source language: EN
    >>> 'Hogy is néz ki a magyar? Elfelejtettem...'
```


## Options

- `-t`, `--target`: target language code
- `-c`, `--content`: content to translate
- `-i`, `--input-file`: read content from a file; use `-` for stdin
- `-e`, `--edit`: compose content in a local editor
- `-s`, `--source`: source language, if you want to override auto-detection
- `-m`, `--more-output`, `--more_output`: include request and language info in
  the output
- `-f`, `--file`: path to a file containing `TRL_API_KEY ...`
- `-k`, `--key`: pass an API key directly on the command line
- `-p`, `--provider`: choose the backend provider
- `--port`: override the default port for a self-hosted provider
- `--base-url`: full base URL for a self-hosted or remote provider
- `--model`: model name for providers that require one, such as `ollama`


## Caveats

- `trl` does not validate that the selected API key matches the selected
  provider.
- Supported languages depend on the provider you use.
- Short or ambiguous input may translate differently depending on whether you
  specify `--source`.

Example:

```text
$ trl -t EN -c "haine"
haine
$ trl -t EN -c "haine" -s FR
hate
```


## Further info

- [ISO 639-1 language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
  in use by DeepL's API. You may also be able to use full written-out language
  names with language models in the Ollama provider.
- [DeepL API documentation](https://developers.deepl.com/docs/getting-started/about).
  They also offer a [CLI API client](https://github.com/DeepLcom/deepl-cli) with
  more features than this project has, however `trl` has existed for longer. 🙂
- [LibreTranslate documentation](https://docs.libretranslate.com/)
- [Ollama](https://ollama.com/)
- [Open a new issue](https://github.com/lmerz1/trl/issues/new)

The author is not affiliated with DeepL SE or any of the other translation
providers.
