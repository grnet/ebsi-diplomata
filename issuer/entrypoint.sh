#!/bin/bash

HOST=0.0.0.0
PORT=7000

until pg_isready -h ${SQL_HOST} -p ${SQL_PORT}; do 
    echo "Connecting to database..."
    sleep 2
done

create-did

python3 manage.py makemigrations --noinput
python3 manage.py makemigrations core --noinput
python3 manage.py migrate --noinput
python3 manage.py runserver ${HOST}:${PORT}

exec "$@"
