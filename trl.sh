#!/bin/zsh

############################################################
# Written starting from 2023-05                            #
############################################################

############################################################
# Helper functions                                         #
############################################################

function help()
{
   echo "Translate phrases quickly using DeepL"
   echo "Dependency: jq for processing the response JSON"
   echo "Registration for an API key is free, but required for this program."
   echo "(https://deepl.com/api)"
   echo
   echo "Syntax: trl [-t|h|c]"
   echo "options:"
   echo "h     Print this help."
   echo "t     Two-letter target language code, ex. FR, ES, DE, ..."
   echo "c     Content to be translated."
   echo "      Escape with surrounding \" double quotes, optional for single words!"
   echo
}

# True if $1 is an executable in $PATH
# Works in both {ba,z}sh
function is_bin_in_path {
  if [[ -n $ZSH_VERSION ]]; then
    builtin whence -p "$1" &> /dev/null
  else  # bash:
    builtin type -P "$1" &> /dev/null
  fi
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
# Read API key from file and perform a (basic) check       #
############################################################

auth_key=$(awk '$1 == "deepl_auth_key" { print $2 }' ./API_KEY.txt)
if [[ ! -n $auth_key ]] then
   echo "Please set a valid DeepL authentication key in API_KEY.txt"
   echo "Use trl -h for further information."
   exit
fi

############################################################
# Check dependency's availability, exit with notice if not #
############################################################

if ! is_bin_in_path jq; then
   echo "This tool requires jq (https://stedolan.github.io/jq/)."
   echo "Install it please, and then run this tool again."
   echo "Use trl -h for further information."
   exit
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

