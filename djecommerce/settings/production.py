from .base import *

DEBUG = config('DEBUG', cast=bool)
ALLOWED_HOSTS = ['84.216.113.116']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': ''
    }
}

#STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY')
#STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY')

STRIPE_PUBLISHABLE_KEY = 'pk_test_51Ht9JcFRP5ucPaMMxdHhH9rp249fcT9zlP00wRkCookqJa608VFDhuqwd0856jxvbLYWuj2GCQgppBiSj70sgHJ800H96vkyJa'
STRIPE_SECRET_KEY = 'sk_test_51Ht9JcFRP5ucPaMMXCMIaejaHxqLaCd30RxKmoQQoM3aNGls3zn0y76wP8RYUlwUKjCpZgavXzfXAAQDvczKzBrf00bpWh0xtB'
STRIPE_ENDPOINT_SECRET = 'whsec_1uBkFTF0jrGrdmEcq5v4Mf1P5pc87FjR'
