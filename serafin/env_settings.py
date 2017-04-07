# coding: utf-8
import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

LANGUAGE_CODE = 'nb'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': 'rds-ssl-ca-cert.pem'
        }
    },
    'vault': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': 'rds-ssl-ca-cert.pem'
        }
    }
}

USE_HTTPS = True
HTTP_HOST = os.environ.get('SERVER_NAME')

DEBUG = False

USERDATA_DEBUG = True

# E-mail settings

ADMINS = (
    ('Eirik', 'eirik@inonit.no'),
    ('Rolf', 'rolf.blindheim@inonit.no'),
)
SERVER_EMAIL = 'Endre <post@inonit.no>'
DEFAULT_FROM_EMAIL = 'Endre <post@inonit.no>'
EMAIL_SUBJECT_PREFIX = '[Endre] '
EMAIL_HOST_USER = os.environ.get('SMTP_USER')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_HOST = os.environ.get('SMTP_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Twilio

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')
