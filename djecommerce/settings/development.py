from .base import *

DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

""" STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY_VAR')
STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY_VAR')
STRIPE_ENDPOINT_SECRET = config('STRIPE_ENDPOINT_SECRET_KEY') """

STRIPE_PUBLIC_KEY = os.environ['STRIPE_LIVE_PUBLIC_KEY_VAR']
STRIPE_SECRET_KEY = os.environ['STRIPE_LIVE_SECRET_KEY_VAR']
STRIPE_ENDPOINT_SECRET = os.environ['STRIPE_ENDPOINT_SECRET_KEY']
