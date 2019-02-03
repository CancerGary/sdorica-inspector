#!/bin/sh
cd `dirname $0`
eval $(ps -ef | grep "[0-9] /home/sdorica-inspector" | awk '{print "kill "$2}')
# run as background process
pipenv run gunicorn backend.wsgi --log-file gunicorn.log --daemon
pipenv run celery -A backend.api.celery worker --loglevel=info --logfile=celery.log --concurrency=4 --detach