#!/usr/bin/env bash
cd `dirname $0`
kill `ps auxww | grep 'celery worker' | grep -v 'grep' | awk '{print $2}'`
kill -9 `ps auxww | grep 'gunicorn' | grep -v 'grep' | awk '{print $2}'`
# run as background process
pipenv run gunicorn backend.wsgi --log-file gunicorn.log --daemon
pipenv run celery -A backend.api.celery worker --loglevel=info --logfile=celery.log --concurrency=4 --detach