import os
from .common import *
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()


DEBUG = False
# after deploying to production, you should change the * in allowed_hosts to your domain name
ALLOWED_HOSTS = ['*']
SECRET_KEY = os.environ['SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DB_NAME'],
        'HOST': os.environ['DB_HOST'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'PORT': os.environ['DB_PORT'],
    }
}