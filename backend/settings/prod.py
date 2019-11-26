""" Production Settings """

import os
import secrets

import dj_database_url
from .dev import *

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except:
    pass
############
# DATABASE #
############
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}

############
# SECURITY #
############

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(64))

DEBUG = False
# Set to your Domain here (eg. 'django-vue-template-demo.herokuapp.com')
ALLOWED_HOSTS = ['*']
