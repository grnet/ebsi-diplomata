#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

Trigger DID creation for the service running at the provided address.

You will be asked to pass an EBSI token needed for DID registration. EBSI
tokens tokens are taken from https://app.preprod.ebsi.eu/users-onboarding and
expire after 15 mins.

Options:
  --host                              Service host. Default: localhost
  -p, --port                          Listening port. Default: 7000
  -a, --algo [Ed25519|Secp256k1|RSA]  Keygen algorithm. Default: Secp256k1
  -h, --help                          Display help message and exit
"

usage() { echo -n "$usage_string" 1>&2; }

HOST=localhost
PORT=7000
EBSI_TOKEN=
ALGO=Secp256k1

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        --host)
            HOST="$2"
            shift
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift
            shift
            ;;
        -a|--algo)
            case "$2" in
                Ed25519|Secp256k1|RSA)
                    ALGO="$2"
                    shift
                    ;;
                *)
                    echo "[-] Unknown keygen algorithm: ${2}"
                    usage
                    exit 1
            esac
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


REMOTE="${HOST}:${PORT}"


read -p "Give token: " token
EBSI_TOKEN=$token

curl -vX PUT "${REMOTE}/api/v1/did/create/" \
    -H "Content-Type: application/json" \
    -d "{\"token\": \"${EBSI_TOKEN}\", \"algo\": \"${ALGO}\", \"onboard\": true}"
