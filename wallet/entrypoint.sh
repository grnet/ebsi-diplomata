#!/bin/bash

set -e

cat init-db.sql | sqlite3 ${DBNAME}   # TODO

python3 src                           # TODO

exec "$@"
