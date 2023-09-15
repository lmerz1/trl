# trl

Translate efficiently on the command line using DeepL:

Rudimentary (!) first version of a shortcut to using DeepL's API in a shell.
If you use this for your day-to-day, human-not-machine translation desires, no major issues should occur with the API requests.

**Providing your own API key by signing up for free with [DeepL](https://www.deepl.com/en/pro-api?cta=header-pro-api/) is necessary for this to function.**


Once you have your own API key, please enter it into the API_KEY.txt file in the following format:

    deepl_auth_key your-api-key-here:fx


## Valid uses – examples

Both the target language (`-t`) and the content of the string to be translated (`-c`) must be specified.

    trl -h
    trl -t es -c "Hallo Welt! Wie geht's?"
    trl -c "How does Hungarian work again..." -t "HU"
    
    

Example output:

    ~ % trl -c "Can my terminal display a Japanese script?" -t ja
    端末に日本語を表示できますか？ 
    ~ % 

and with -f:

    ~ % trl -c "How does Hungarian work again? I forgot..." -t HU -f

        Request:
        Target language: HU
        >>> 'How does Hungarian work again? I forgot...'

        Answer:
        Detected source language: EN
        >>> 'Hogy is működik a magyar? Elfelejtettem...'

    ~ %


## Dependencies

Currently using [jq](https://stedolan.github.io/jq/) for processing the response JSON


## Further info

For more detailed documentation, check out [DeepL's API](https://www.deepl.com/en/docs-api/introduction/) as well as the [list of ISO 639-1 language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) which are used for abbreviating the target language.

 Not affiliated in any way with DeepL SE, but appreciative of their free API.


