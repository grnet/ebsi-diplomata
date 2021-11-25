#!/bin/bash

usage_string="usage: ./$(basename "$0") --token <TOKEN> [--did <DID>]

DID onboarding and registering to the EBSI.

IMPORTANT: Tokens are taken in raw format from 

https://app.preprod.ebsi.eu/users-onboarding

and expire after 15 minutes.

Options:
  -d, --did DID         DID to onboard. If not specified, the last created DID will
                        be used; exit with 2 if no DID exists.
  --token FILE          File containing the bearer token. Defaults to

                        ${WALTDIR}/data/ebsi/bearer-token.txt
  
                        Exit with 2 if expired.
  --resolve             Resolve registered DID to check if it was correctly anchored.

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

check_token_expire() {
    resp=$1
    if echo $resp | grep -q "invalid_jwt: JWT has expired"; then
        echo "Failed: Token has expired"
        exit 2
    fi
}

set -e

EBSI_PRFX="did:ebsi"
RESOLVE=false
TOKEN="${WALTDIR}/data/ebsi/bearer-token.txt"
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
        --resolve)
            RESOLVE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
    esac
done

cd ${WALTDIR}

if [ -z ${DID} ]; then
    DID=$(get_last_did)
fi

resp=$(./ssikit.sh essif onboard --did ${DID} ${TOKEN})
check_token_expire $resp
echo $resp
# echo "[+] DID onboarded"

resp=$(./ssikit.sh essif auth-api --did ${DID})
echo $resp
# echo "[+] EBSI Auth API flow executed"

resp=$(./ssikit.sh essif did register --did ${DID})
echo $resp
# echo "[+] DID registered to EBSI"

if [ ${RESOLVE} == true ]; then
    resp=$(./ssikit.sh did resolve --did ${DID})
    echo $resp
    # echo "[+] Registered DID has been resolved"
fi


STORAGE_EBSI="${STORAGE_EBSI}/ebsi"
mkdir -p ${STORAGE_EBSI}
cp -r "data/ebsi/${DID#"$EBSI_PRFX:"}" "${STORAGE_EBSI}/"
