#!/bin/bash

HOST=0.0.0.0
PORT=7001

python3 manage.py makemigrations --noinput
python3 manage.py makemigrations core --noinput
python3 manage.py migrate --noinput
python3 manage.py runserver ${HOST}:${PORT}

exec "$@"
