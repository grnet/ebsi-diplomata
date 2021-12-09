#!/bin/bash

HTTP_HOST=0.0.0.0

until pg_isready -h ${SQL_HOST} -p ${SQL_PORT}; do 
    echo "Connecting to database..."
    sleep 2
done

python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput
python3 manage.py runserver ${HTTP_HOST}:${HTTP_PORT}

exec "$@"
