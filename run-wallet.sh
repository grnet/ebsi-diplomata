#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

Wallet driver script. TODO

Options:
  --build       Build image before running the app 
  --only-build  Build image without running app
  -h, --help    Display help message and exit

Examples:
"

usage() { echo -n "$usage_string" 1>&2; }

IMAGE=wallet
CONTAINER=wallet
WORKDIR=/home/wallet/app

DO_BUILD=false
DO_RUN=true

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
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
    docker container rm "${CONTAINER}"
    docker run \
        --name ${CONTAINER} \
        --volume ${PWD}/wallet:/${WORKDIR} \
        --volume ${PWD}/storage/wallet:/home/wallet/storage \
        --volume ${PWD}/commands:/usr/local/sbin \
        --network=host \
        --interactive \
        --tty \
        ${IMAGE}:latest
fi