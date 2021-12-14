#!/bin/bash

TOKEN=$1
ALGO=Ed25519
ONBOARD=false

curl -X PUT localhost:7000/api/v1/did/create/ \
    -H "Content-Type: application/json" \
    -d "{\"token\": \"${TOKEN}\", \"algo\": \"${ALGO}\", \"onboard\": ${ONBOARD}}"

echo
