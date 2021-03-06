#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

Run the wallet container and optionally build the image.

Options:
  --name        Container name. Defaults to \"holder\".
  --issuer      Issuer service to connect. Default: http://localhost:7000
  --verifier    Verifier service to connect. Default: http://localhost:7001
  --build       Build wallet image before running the application (will also
                re-build the base image)
  -h, --help    Display help message and exit

Examples:
"

usage() { echo -n "$usage_string" 1>&2; }

IMAGE=ebsi-wallet-dev
CONTAINER=holder
WORKDIR=/home/dev/app
STORAGE=/home/dev/storage
DBNAME=${STORAGE}/${CONTAINER}.db
ISSUER_ADDRESS=
VERIFIER_ADDRESS=

DO_BUILD=false

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        --name)
            CONTAINER="$2"
            shift
            shift
            ;;
        --issuer)
            ISSUER_ADDRESS="$2"
            shift
            shift
            ;;
        --verifier)
            VERIFIER_ADDRESS="$2"
            shift
            shift
            ;;
        --build)
            DO_BUILD=true
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

if [ ${DO_BUILD} == true ]; then
    ./build-base-image.sh --tag "local" --no-push
    docker image build \
        -t ${IMAGE} \
        -f Dockerfile.wallet.dev \
        .
fi

docker container rm "${CONTAINER}" >/dev/null
docker run \
    --name ${CONTAINER} \
    --network=host \
    -v ${PWD}/wallet:/${WORKDIR} \
    -v ${PWD}/storage/wallet:${STORAGE} \
    -v ${PWD}/ssi-lib/commands:/usr/local/sbin \
    -e ISSUER_ADDRESS=${ISSUER_ADDRESS} \
    -e VERIFIER_ADDRESS=${VERIFIER_ADDRESS} \
    -e DBNAME=${DBNAME} \
    -it \
    ${IMAGE}:latest
