import os
from .common import *
import os
from dotenv import load_dotenv

load_dotenv()


DEBUG = False
ALLOWED_HOSTS = ['django-app-env.eba-dnjkhspu.us-west-2.elasticbeanstalk.com']
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