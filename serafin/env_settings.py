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

SMS_SERVICE = 'Twilio'
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')


HUEY = {
    'name': 'serafin',
    'store_none': True,
    'always_eager': False,
    'consumer': {
        'quiet': True,
        'workers': 64,
        'worker_type': 'greenlet',
        'health_check_interval': 60,
    },
    'connection': {
        'host': os.environ.get('REDIS_HOST'),
        'port': int(os.environ.get('REDIS_PORT', 6379))
    }
}

MIDDLEWARE_CLASSES = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'users.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'events.middleware.EventTrackingMiddleware',
)

AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_BUCKET')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = 'eu-central-1'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

COMPRESS_ENABLED = False

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CONSTANCE_REDIS_CONNECTION = {
    'host': os.environ.get('REDIS_HOST'),
    'port': int(os.environ.get('REDIS_PORT', 6379))
}

GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
