#!/bin/zsh

############################################################
# Written on 2023-05-16                                    #
############################################################

auth_key='paste_your_auth_key_here:fx'

############################################################
# Help                                                     #
############################################################

help()
{
   echo "Translate phrases quickly using DeepL"
   echo "Dependency: jq for processing the response JSON"
   echo
   echo "Syntax: trl [-t|h|c]"
   echo "options:"
   echo "h     Print this help."
   echo "t     Two-letter target language code (FR, ES, DE, ...)"
   echo "c     Content to be translated (escape with surrounding \" double quotes!"
   echo "      not necessary for single words.)"
   echo
}

############################################################
# Main program                                             #
############################################################

############################################################
# Process the input options.                               #
############################################################

if [[ $1 == "" ]]; then
    help;
    exit;
else
   while getopts "ht:c:" option; do
      case $option in
         h) # display Help
            help
            exit;;
         t) # Enter target language
            target=$OPTARG;;
         c) # Enter string to be translated
            content=$OPTARG;;
        \?) # Invalid option
            echo "Error: Invalid option. Use trl -h for help"
            exit 1;;
      esac
   done
fi

############################################################
# Send translation request to the API and print response   #
############################################################

echo
echo "    Request:"
echo "    Target language: $target"
echo "    >>> '$content'"
echo

response=$(curl -s -X POST 'https://api-free.deepl.com/v2/translate' \
         -H 'Authorization: DeepL-Auth-Key '"$auth_key" \
         -d text=$content \
         -d target_lang=$target)

answer_text=$(jq -r  '.translations[0].text' <<< "${response}")
source_lang=$(jq -r '.translations[0].detected_source_language' <<< "${response}")

echo "    Answer:"
echo "    Detected source language: $source_lang"
echo "    >>> '$answer_text'"
echo 

