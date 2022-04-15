#!/bin/bash

usage_string="usage: ./$(basename "$0") [OPTIONS]

Options:
 --host         Service host (default: 0.0.0.0)
 --port         Service listening port (default: env var PORT)
 --workers      Number of workers (default: 2)
 --no-gunicorn  Do not run with gunicorn (default: false)
 -h, --help     Display help message and exit
"

usage() { echo -n "$usage_string" 1>&2; }

GUNICORN=true
NR_WORKERS=4
HOST=0.0.0.0
PORT=${PORT}

while [[ $# -gt 0 ]]
do
    arg="$1"
    case $arg in
        --host)
            HOST="$2"
            shift
            shift
            ;;
        --port)
            PORT="$2"
            shift
            shift
            ;;
        --workers)
            NR_WORKERS="$2"
            shift
            shift
            ;;
        --no-gunicorn)
            GUNICORN=false
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


until pg_isready -h ${SQL_HOST} -p ${SQL_PORT}; do 
    echo "Connecting to database..."
    sleep 2
done

python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput


if [[ ${GUNICORN} == true ]]; then

    gunicorn web_project.wsgi:application \
        --workers ${NR_WORKERS} \
        --bind ${HOST}:${PORT} \
        --preload \
        --reload
else
    python3 manage.py runserver ${HOST}:${PORT}
fi

exec "$@"
