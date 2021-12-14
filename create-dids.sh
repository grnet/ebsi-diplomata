#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

Perform DID creation PUT requests for the services running at localhost:7000-1

You will be asked to optionally pass an EBSI token needed for DID registration.
EBSI tokens are taken from https://app.preprod.ebsi.eu/users-onboarding and
expire after 15 minutes.

Newly created DIDs will not be stored if they fail to be registered. Note that 
a DID fails to be registered if no token is provided or if the provided token 
is either invalid or expired. 

Use the --no-register option if you want to have newly created DIDs stored but
not registered.

WARNING: a non-registered DID fails to be resolved by interested parties and
thus be effectively involved in protocol operations.

Options:
  --algo [Ed25519|Secp256k1]    Keygen algorithm. Default: Ed25519
  --no-register                 Force creation of DIDs without registering them
                                to the EBSI. See WARNING above.
  -h, --help                    Display help message and exit
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
    echo -ne "\nDo you want to provide an EBSI Token? (y/n) "
    yes=$(parse_yes_no)
    if [ ${yes} == true ]; then
        read -p "Give token: " token
        EBSI_TOKEN=$token
    fi
}

do_put_request() {
    port=$1
    addr=localhost:${port}
    payload="{\"token\": \"${EBSI_TOKEN}\", \"algo\": \"${ALGO}\", 
      \"onboard\": ${ONBOARD}}"
    echo -ne "\nWaiting response from ${addr} ...\n"
    curl -X PUT "${addr}/api/v1/did/create/" \
        -H "Content-Type: application/json" \
        -d "${payload}"
}

EBSI_TOKEN=
ALGO=Ed25519
ONBOARD=true

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        --algo)
            if [ "$2" == "Ed25519" ] || [ "$2" == "Secp256k1" ]; then
                ALGO="$2"
            else
                echo "[-] Unrecongized keygen algorithm: ${2}"
                usage
                exit 1
            fi
            shift
            shift
            ;;
        --no-register)
            ONBOARD=false
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

if [ ${ONBOARD} == true ]; then
    parse_token
fi

if [ ${ONBOARD} == true ] && [ -z ${EBSI_TOKEN} ]; then
    echo -ne "\nWARNING: You have provided no EBSI token. This means that"
    echo -ne "\nnewly created DIDs will not be registred to the EBSI."
    echo -ne "\nProceed? (y/n) "
    yes=$(parse_yes_no)
    if [ ${yes} == false ]; then
        echo -ne "\nAborted\n"
        exit 1
    fi
fi

do_put_request 7000
do_put_request 7001
echo
