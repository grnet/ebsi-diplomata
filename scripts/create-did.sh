#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

DID creation

Convenience wrapper of the \`./ssikit.sh did create [...]\` command.

Arguments (mandatory):
  --name  NAME                    The generated DID will be exported to
                                  ${STORAGE}/dids/<NAME>.json
                                  Existing files are overwritten.
Options:
  -k, --key                       Specific key (ID or alias). If not provided,
                                  a newly created key will be used, which will 
                                  be generated according to an algorithm
                                  specified as follows.
  -a, --algo [Ed25519|Secp256k1]  Keygen algorithm. Default: Ed255519
"

usage() { echo -n "$usage_string" 1>&2; }

get_nr_keys() {
    NR_KEYS=$(./ssikit.sh key list | grep -c "\- [0-9]*:")
    echo $NR_KEYS
}

get_last_key() {
    NR_KEYS=$(get_nr_keys)
    KEY=$(./ssikit.sh key list \
        | grep "\- ${NR_KEYS}:" \
        | awk -F' ' '{print $3}' \
        | tr -d '"')
    echo $KEY
}

set -e

KEY=
ALGO=Ed25519
NAME=

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        -a|--algo)
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
        -k|--key)
            KEY="$2"
            shift
            shift
            ;;
        --name)
            NAME="$2"
            shift
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
    esac
done

if [ -z ${NAME} ]; then
    echo "[-] No name specified"
    usage && exit 1
fi

OUTFILE="${STORAGE}/dids/${NAME}.json"

cd ${WALTDIR}

if [ -z ${KEY} ]; then
    ./ssikit.sh key gen --algorithm ${ALGO}
    KEY=$(get_last_key)
fi

./ssikit.sh did create \
    --did-method ebsi \
    --key ${KEY} \
    --out ${OUTFILE}
