# trl

Translate efficiently on the command line using DeepL:

Rudimentary (!) first version of a shortcut to using DeepL's API in a shell.
If you use this for your day-to-day, human-not-machine translation desires, no major issues should occur with the API requests.

**Providing your own API key by signing up for free with [DeepL](https://www.deepl.com/en/pro-api?cta=header-pro-api/) is necessary for this to function.**


## Valid uses – examples
    trl -h
    trl -t ES -c "Hallo Welt! Wie geht's?"
    trl -c "How does Hungarian work again..." -t "HU"
    
    

Example output:

    ~ % trl -c "How does Hungarian work again? I forgot..." -t HU

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

For more detailed documentation, check out [DeepL's API](https://www.deepl.com/en/docs-api/introduction/) as well as the [list of ISO 639-1 country codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) which are used for abbreviating the target language.

 Not affiliated in any way with DeepL SE, but appreciative of their free API.


