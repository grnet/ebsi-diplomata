#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

Run the issuer and verifier services at localhost:7000-1 respectively.

Options:
  --build       Build web image before running the application (will also
                re-build the base image)
  -h, --help    Display help message and exit

Examples:
"

usage() { echo -n "$usage_string" 1>&2; }

DO_BUILD=false
compose_args=()

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        --build)
            DO_BUILD=true
            compose_args+=($arg)
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
    ./build-base-images.sh \
        --tag "local" \
        --no-push
fi

# TODO: Give values after google oauth setup
export EBSI_DIPLOMAS_GOOGLE_CLIENT_ID=
export EBSI_DIPLOMAS_GOOGLE_CLIENT_SECRET=
export EBSI_DIPLOMAS_GOOGLE_TOKEN_URL=
export EBSI_DIPLOMAS_GOOGLE_AUTHORIZE_URL=
export EBSI_DIPLOMAS_GOOGLE_API_BASE_URL=
export EBSI_DIPLOMAS_GOOGLE_SERVER_METADATA_URL=
export EBSI_DIPLOMAS_GOOGLE_SCOPE=

docker-compose up $compose_args \
    --remove-orphans
