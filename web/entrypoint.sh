#!/bin/bash

HTTP_HOST=0.0.0.0

until pg_isready -h ${SQL_HOST} -p ${SQL_PORT}; do 
    echo "Connecting to database..."
    sleep 2
done

if [ -z "$(ls -A ${STORAGE}/did)" ]; then
    create-did > /dev/null
fi

# TODO: Make these persistent
cd /home/web
create-key --export key.json
create-did --key $(get-key) --export did.json
cd -

python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput
python3 manage.py runserver ${HTTP_HOST}:${HTTP_PORT}

exec "$@"
