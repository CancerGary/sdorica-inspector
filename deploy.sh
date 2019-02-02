#!/bin/sh
pipenv install
pipenv run python manage.py migrate
yarn install
pipenv run python manage.py collectstatic --noinput