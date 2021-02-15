from .base import *

DEBUG = False
ALLOWED_HOSTS = ['84.216.113.116', '127.0.0.1']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': ''
    }
}

""" STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY_VAR')
STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY_VAR')
STRIPE_ENDPOINT_SECRET = config('STRIPE_ENDPOINT_SECRET_KEY') """

STRIPE_PUBLIC_KEY = os.environ['STRIPE_LIVE_PUBLIC_KEY_VAR']
STRIPE_SECRET_KEY = os.environ['STRIPE_LIVE_SECRET_KEY_VAR']
STRIPE_ENDPOINT_SECRET = os.environ['STRIPE_ENDPOINT_SECRET_KEY']
