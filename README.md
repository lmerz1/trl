# trl

Translate phrases quickly and efficiently on the command line using DeepL: A wrapper to using DeepL's API in a shell.

If you want to use this for your day-to-day translation needs, no major issues should occur with API request limits.

**Providing your own API key by signing up for free with [DeepL](https://www.deepl.com/en/pro-api?cta=header-pro-api/) is necessary for this to work.**


## How to get

Download and add the script file to your `$PATH`. It features a shebang, to avoid having to call it with `python3 trl.py` or similar.

```sh
# While in a directory that is part of your path
curl https://raw.githubusercontent.com/lmerz1/trl/main/trl > trl && chmod +x trl
```

Once you have your own API key, export it as an environment variable, for example in your `.{ba,z,…}shrc` file:

```sh
export DEEPL_API_KEY="your-api-key-here:fx"
```

Alternatively, please enter it into a separate text file in the following format, on a new line, and use the `-f` flag to supply the path to this file:
- In the file, put: `DEEPL_API_KEY your-api-key-here:fx`
- Using it, add the option: `-f /path/to/API_KEYS.txt`


## Dependencies

`trl` is a basic Python script. It needs:
- Any `python3` version (this is technically untested, but any _should_ work)
- The `requests` module, i.e. `pip install requests`


## Options

`-t`, `--target`: Two-letter ISO 639-1 language code – check with DeepL which languages are currently supported (links [below](#further-info))

`-c`, `--content`: The content to be translated.

`-s`, `--source`: (optional) Specfiy the source language, if necessary, for more accurate translations.

`-m`, `--more_output`: (optional) Enable a fancier, longer output formatting including the input and language detection info.
                       Default output is the pure response text and nothing else.


## Valid uses – examples

Both the target language (`-t`) and the content of the string to be translated (`-c`) **must** be specified.

```sh
trl -h
trl -t ES -c "Hallo Welt! Wie geht's?"
trl -c "What does Hungarian look like again..." -t "hu"
echo "hello world"|trl -tfr
trl -t en < query.txt > output.txt
```


Example output:

```sh
~ % trl -c "Can my terminal display a Japanese script?" -t JA
端末に日本語を表示できますか？ 
~ % 
```

and with `-m`:

```
~ % trl -c "What does Hungarian look like again? I forgot..." -t hu -m

    Request:
    Target language: HU
    >>> 'What does Hungarian look like again? I forgot...'

    Answer:
    Detected source language: EN
    >>> 'Hogy is néz ki a magyar? Elfelejtettem...'

~ % 
```

Typically, source language detection works flawlessly.
However, there are cases where the translated result differs depending on the source language, which DeepL might not be able to unambiguously recognize.
This can especially occur if shorter phrases or single words are to be translated, as in the following example.

In such cases, a specific source language (`-s`) in the request **can** also be specified:

```
$ trl -mt en -c uger     

    Request:
    Target language: EN
    >>> 'uger'

    Answer:
    Detected source language: EN
    >>> 'uger'

$ trl -mt en -c uger -s da

    Request:
    Target language: EN
    >>> 'uger'

    Answer:
    Supplied source language: DA
    >>> 'weeks'

$
```

This would of course also work without the `-m` flag's increased output/"fancy" formatting, but it has been included above as to demonstrate the difference in processing and output:

```sh
$ trl -ten -c uger  
uger
$ trl -ten -c uger -sda
weeks
```


## Further info

For more detailed documentation, see the list of [ISO 639-1 language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) which are used for abbreviating the target language.
Check with [DeepL](https://www.deepl.com/en/docs-api/introduction/) which languages are currently supported.

Not affiliated in any way with DeepL SE, but appreciative of their free API offering.

