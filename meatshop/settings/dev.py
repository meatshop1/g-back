from .common import *
import os
from dotenv import load_dotenv



load_dotenv()


DEBUG = True
SECRET_KEY = 'django-insecure-&r%wiycqoat+yr+$@z4zimi(e!2oxn!(*p8z=zbjagwv-6t12q'
ALLOWED_HOSTS = ['*']

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'meatshop',
#         'HOST': 'localhost',
#         'USER': os.environ['LOCAL_DB_USER'],
#         'PASSWORD': os.environ['LOCAL_DB_PASSWORD'],
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DB_NAME'],
        'HOST': os.environ['LOCAL_DB_HOST'],
        'USER': os.environ['LOCAL_DB_USER'],
        'PASSWORD': os.environ['LOCAL_DB_PASSWORD'],
        'PORT': os.environ['DB_PORT'],
    }
}

