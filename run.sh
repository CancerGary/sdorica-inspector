#!/bin/sh
cd `dirname $0`
eval $(ps -ef | grep "[0-9] /home/sdorica-inspector" | awk '{print "kill "$2}')
nohup pipenv run gunicorn backend.wsgi --log-file gunicorn.log &
nohup pipenv run celery -A backend.api.celery worker --loglevel=info --logfile=celery.log --concurrency=4 &