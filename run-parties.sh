#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

Run issuer and verifier at localhost:7000-7001 respectively.

You will be asked to optionally pass an EBSI token needed for DID registration
during service setup. Note that, for each service, the corresponding DID is 
persistently stored, in which case it needs not be recreated (unless forced).

Tokens for the preprod EBSI taken from: https://app.preprod.ebsi.eu/users-onboarding

Options:
  --force-did                   Force creation of new DIDs. Default: false
  --algo [Ed25519|Secp256k1]    Keygen algorithm. A new key will be created
                                in case no persistently stored DIDs is avaiable
                                or creation of new DIDs has been forced.
                                Default: Ed255519
  -h, --help                    Display help message and exit

Examples:
"

usage() { echo -n "$usage_string" 1>&2; }

parse_yes_no() {
    read yn
    if [[ "$yn" != "${yn#[Yy]}" ]]; then
        echo true
    else
        echo false
    fi
}

parse_token() {
    echo -ne "\n Do you want to provide an EBSI Token? (y/n) "
    yes=$(parse_yes_no)
    if [ ${yes} == true ]; then
        read -p " Give token: " token
        EBSI_TOKEN=$token
    fi
}

set -e

COMPOSE_FILE="docker-compose.yml"
FORCE_DID=0   # false
KEYGEN_ALGO=Ed25519
EBSI_TOKEN=

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        --algo)
            if [ "$2" == "Ed25519" ] || [ "$2" == "Secp256k1" ]; then
                KEYGEN_ALGO="$2"
            else
                echo "[-] Unrecongized keygen algorithm: ${2}"
                usage
                exit 1
            fi
            shift
            shift
            ;;
        --force-did)
            FORCE_DID=1   # set true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "[-] Invalid argument: $arg"
            usage
            exit 1
            ;;
    esac
done

parse_token

if [ -z ${EBSI_TOKEN} ] && [ ${FORCE_DID} == 1 ]; then
    echo -ne "\n WARNING: You have forced DID creation without having provided"
    echo -ne "\n an EBSI token. This means that newly created DIDs will not be"
    echo -ne "\n properly registered to the EBSI. Proceed? (y/n) "
    yes=$(parse_yes_no)
    if [ ${yes} == false ]; then
        echo -ne "\n Aborted\n"
        exit 1
    fi
fi

export WEB_EBSI_TOKEN=$EBSI_TOKEN
export WEB_KEYGEN_ALGO=$KEYGEN_ALGO
export WEB_FORCE_DID=$FORCE_DID
echo

docker-compose -f $COMPOSE_FILE up \
    --remove-orphans
