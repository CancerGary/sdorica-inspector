""" Production Settings """

import os
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

DEBUG = False
# Set to your Domain here (eg. 'django-vue-template-demo.herokuapp.com')
ALLOWED_HOSTS = ['*']

# for audio file, may be replaced
WHITENOISE_AUTOREFRESH = True