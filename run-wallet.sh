#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

Wallet driver script. TODO

Options:
  --name        Container name. Defaults to holder.
  --build       Build image before running the app 
  --only-build  Build image without running app
  -h, --help    Display help message and exit

Examples:
"

usage() { echo -n "$usage_string" 1>&2; }

IMAGE=wallet
CONTAINER=holder
WORKDIR=/home/wallet/app            # See Dockerfile.wallet
STORAGE=/home/wallet/storage        # See Dockerfile.wallet
DBNAME=${STORAGE}/${CONTAINER}.db

DO_BUILD=false
DO_RUN=true

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        --name)
            CONTAINER="$2"
            shift
            shift
            ;;
        --build)
            DO_BUILD=true
            shift
            ;;
        --only-build)
            DO_BUILD=true
            DO_RUN=false
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
    docker image build \
        -t ${IMAGE} \
        -f Dockerfile.wallet \
        .
fi

if [ ${DO_RUN} == true ]; then
    docker container rm "${CONTAINER}" >/dev/null
    docker run \
        --name ${CONTAINER} \
        --network=host \
        -v ${PWD}/wallet:/${WORKDIR} \
        -v ${PWD}/storage/wallet:${STORAGE} \
        -v ${PWD}/ssi-lib/commands:/usr/local/sbin \
        -e DBNAME=${DBNAME} \
        --interactive \
        --tty \
        ${IMAGE}:latest
fi
