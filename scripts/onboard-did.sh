#!/bin/bash

usage_string="usage: ./$(basename "$0") --token <TOKEN> [--did <DID>]

DID onboarding to the EBSI.

Convenience wrapper of the \`./ssikit.sh essif onboard [...]\` command.

NOTE: After onboarding a DID called <DID>, the relevant verifiable 
authorization can be found at

  ${STORAGE}/ebsi/<DID>/verifiable-authorization.json

Arguments (mandatory):
  --token FILE          File containing the bearer token. Exit with 2 if expired.
                        IMPORTANT: Tokens are taken in raw format from 

                        https://app.preprod.ebsi.eu/users-onboarding/authentication

                        and expire after 15 minutes.
Options:
  -d, --did DID         DID to onboard. If not specified, the last created DID will
                        be used; if no DID exists, exit with 2.

Examples
  $ $(basename "$0") --token data/ebsi/bearer-token.txt
  $ $(basename "$0") --token data/ebsi/bearer-token.txt --did zjmoeYH3t3FQn93qTqLUQ9j 
"

usage() { echo -ne "$usage_string" 1>&2; }

get_nr_dids() {
    NR_DIDS=$(./ssikit.sh did list | grep -c "\- [0-9]*:")
    echo $NR_DIDS
}

get_last_did() {
    NR_DIDS=$(get_nr_dids)
    if [ ${NR_DIDS} == 0 ]; then
        echo "No created DIDs found." && exit 2
    fi
    DID=$(./ssikit.sh did list \
        | grep "\- ${NR_DIDS}:" \
        | awk -F' ' '{print $3}' \
        | tr -d '"')
    echo $DID
}

set -e

EBSI_PRFX="did:ebsi"
TOKEN=
DID=

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        --token)
            TOKEN="$2"
            shift
            shift
            ;;
        -d|--did)
            if [[ "$2" =~ "$EBSI_PRFX".* ]]; then
                DID="$2"
            else
                DID="$EBSI_PRFX:$2"       # Prepend did:ebsi:
            fi
            shift
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
    esac
done

if [ -z ${TOKEN} ]; then
    echo "[-] No token file specified"
    usage && exit 1
fi

cd ${WALTDIR}

if [ -z ${DID} ]; then
    DID=$(get_last_did)
fi

echo $DID

resp=$(./ssikit.sh essif onboard --did ${DID} ${TOKEN})

if echo $resp | grep -q "invalid_jwt: JWT has expired"; then
    echo "Failed: Token has expired"
    exit 2
else
    DID=${DID#"$EBSI_PRFX:"}               # Strip did:ebsi:
    DID_DIR="${STORAGE}/ebsi/${DID}"
    JSON="verifiable-authorization.json"
    mkdir -p $DID_DIR && cp \
        "data/ebsi/${DID}/${JSON}" "${DID_DIR}/${JSON}"
fi
