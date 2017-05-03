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
    }
}

USE_HTTPS = True
HTTP_HOST = os.environ.get('SERVER_NAME')

DEBUG = False

USERDATA_DEBUG = True


ADMINS = (
    ('Eirik', 'eirik@inonit.no'),
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


SMS_SERVICE = os.environ.get('SMS_SERVICE', 'Twilio')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')

PRIMAFON_KEY = os.environ.get('PRIMAFON_KEY')


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
    # 'request.middleware.RequestMiddleware',
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        }
    },
    'filters': {
        'require_debug': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/eb/serafin.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 3,
            'formatter': 'verbose'
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/eb/debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 0,
            'formatter': 'verbose'
        },
        'huey': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/eb/huey.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 0,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['file', 'console', 'sentry'],
            'propagate': False
        },
        'django.request': {
            'level': 'ERROR',
            'handlers': ['file', 'console', 'sentry'],
            'propagate': False
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        },
        'huey.consumer': {
            'handlers': ['huey', 'sentry'],
            'level': 'INFO',
            'propagate': True,
        },
        'debug': {
            'level': 'DEBUG',
            'handlers': ['debug'],
            'propagate': False
        }
    }
}

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN')
}


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
