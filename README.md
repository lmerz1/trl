# trl

Translate phrases quickly and efficiently on the command line by wrapping around
various translation providers' APIs.

At the moment, the default API used is DeepL.  
If you want to use this for your day-to-day translation needs, no major issues
should occur regarding API request limits with them.

**Providing your own API key by signing up for free with
[DeepL](https://www.deepl.com/en/pro-api?cta=header-pro-api/)
is currently necessary for this to work.**


## How to get started

Download and add the script file to your `$PATH`. For UNIX users, it features a
shebang, to avoid having to call it with `python3 trl.py` or similar.

```sh
# While in a directory that is part of your path
curl https://raw.githubusercontent.com/lmerz1/trl/main/trl > trl && chmod +x trl
```

`trl` will use DeepL by default.
Once you have your own API key (see above), export it as an environment
variable, for example in your `.{ba,z,…}shrc` file:

```sh
export TRL_API_KEY="your-api-key-here"
```
Or, for more convenient swapping between multiple keys/providers:
```sh
export DEEPL_API_KEY_1="your-api-key-here:fx"
export TRL_API_KEY="$DEEPL_API_KEY_1"
```
Or, if you have the key(s) defined somewhere else, only choose which one you want
to use right before the actual request:
```sh
TRL_API_KEY="$DEEPL_API_KEY_1" trl --target EN --content "test"
```

Alternatively, please enter it into a separate text file in the following
format, on a new line, and use the `-f` flag to supply the path to this file:
- In the file, put: `TRL_API_KEY your-api-key-here`
- When using `trl`, add the option: `-f /path/to/API_KEYS.txt`

Speaking of shell and environment variables, if you find yourself often translating
into the same target language, you may set a default in your shell config:
```sh
export TRL_DEFAULT_TARGET_LANG=en  # or EN, or de, or any other available language's code
```


## Dependencies

`trl` is a simple Python script. It needs:
- Any `python3` version (this is technically untested, but any _should_ work)
- The `requests` module, i.e. `pip install requests`

> [!TIP]  
> Should there occur any issues with your Python environment,
> you may also run the script using [uv](https://docs.astral.sh/uv/):
> After downloading, simply define a shell alias of your choice for
> `uv run /path/to/trl`


## Options

- `-t`, `--target`: Two-letter ISO 639-1 language code – check with DeepL which
  languages are currently supported (links [below](#further-info))
- `-c`, `--content`: The content to be translated.
- `-s`, `--source`: (optional) Specify the source language, if necessary, for
  more accurate translations.
- `-m`, `--more_output`: (optional) Enable a fancier, longer output formatting
  including the input and language detection info. Default output is the pure
  response text and nothing else.
- `-f`, `--file`: (optional) Path to the "config" file containing the API key in
  the format described above.
- `-k`, `--key`: (optional) Directly supply the API key to the program. Not
  particularly recommended. Remember to keep track of and/or clean your shell
  history if necessary!

> [!TIP]  
> The different authentication options to pass an API key take precedence in
> the reverse order they are listed here, i.e. `--key` will be selected before
> `--file` which will come before a `TRL_API_KEY` environment/shell variable.

- `-p`, `--provider`: Set the translation service provider. Defaults to DeepL's
  API, which requires a working key.
- `--port`: If the above provider service is accessible on a local machine's
  port. Defaults to 5000, which is `LibreTranslate`'s default port.


## Valid uses – examples

Both the target language (`-t`) and the content of the string to be translated
(`-c`) **must** be specified.

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
However, there are cases where the translated result differs depending on the
source language, which a provider might not be able to unambiguously
recognize.
This can especially occur if shorter phrases or single words are to be
translated, as in the following example cases where DeepL trips. 

In such cases, a specific source language (`-s`) in the request **can** also be specified:

```
$ trl -mt en -c "uger"     

    Request:
    Target language: EN
    >>> 'uger'

    Answer:
    Detected source language: EN
    >>> 'uger'

$ trl -mt en -c "uger" -s da

    Request:
    Target language: EN
    >>> 'uger'

    Answer:
    Supplied source language: DA
    >>> 'weeks'

$
```

This would of course also work without the `-m` flag's increased output/"fancy"
formatting, but it has been included above as to demonstrate the difference in
processing and output:

```sh
$ trl -ten -c uger  
uger
$ trl -ten -c uger -sda
weeks
# another example:
$ trl -t EN -c "haine"                          
haine
$ trl -t EN -c "haine" -s FR
hate
```


## Other caveats

`trl` is very robust and works flawlessly for me on a near-daily basis.  

However, `trl` does not check whether the assigned API key is valid for the
selected provider, so in case multiple providers are ever used, you will have to
keep those separated and, for the active one, updated and current yourself.

At this time, the only actually available translation providers are DeepL and,
if you install and run it locally, a self-hosted version of
[LibreTranslate](https://docs.libretranslate.com/).  
I've got a few more in mind already, but feel free to suggest suitable new
providers or otherwise report any problems or bugs you may encounter!
Simply open a new issue [here](https://github.com/lmerz1/trl/issues/new).


## Further info

For more detailed documentation, see the list of
[ISO 639-1 language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
which are typically used for abbreviating the target language.
Check the [DeepL documentation](https://www.deepl.com/en/docs-api/introduction/)
to see which languages they currently support.
They also have their own [API clients](https://www.github.com/deeplcom/)
available for various languages, which this project does not make use of, since
the exposed functionality is also kept way simpler here. :-)

The author is not affiliated in any way with DeepL SE, but highly appreciative
of their free API offering.

