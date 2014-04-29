'''
Django settings for the serafin project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
'''

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'llzkwh=$&0x2*1u^)1&24%ix+_z$io4!gtxo6cxkg=lxqruaz+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'suit',
    'django.contrib.admin',

    'south',
    'django_extensions',
    'rest_framework',
    'filer',
    'mptt',
    'easy_thumbnails',
    'huey.djhuey',
    'django_user_agents',

    'tokens',
    'users',
    'vault',
    'tasks',
    'events',
    'content',
    'plumbing',
    'system',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    #'events.middleware.EventTrackingMiddleware',
)

ROOT_URLCONF = 'serafin.urls'

WSGI_APPLICATION = 'serafin.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'serafin.db'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'nb'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'conf/locale'),
)

TIME_ZONE = 'Europe/Oslo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_HTTPS = True


# E-mail settings

ADMINS = (
    ('Eirik', 'eirik.krogstad@inonit.no'),
)
SERVER_EMAIL = 'SERAF <post@inonit.no>'
DEFAULT_FROM_EMAIL = 'SERAF <post@inonit.no>'
EMAIL_SUBJECT_PREFIX = '[SERAF] '
EMAIL_HOST_USER = 'AKIAJYR7AW6SXUYTVI2Q'
EMAIL_HOST_PASSWORD = 'AuzX2+v7uGKwnYOupxZLGBsOh+b3RCdKtekyBHPLSxkY'
EMAIL_HOST = 'email-smtp.eu-west-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'staticfiles'),
)


# User model and vault separation

AUTH_USER_MODEL = 'users.User'

VAULT_SERVER_API_URL = 'http://localhost:8000/api/vault/'

VAULT_MIRROR_USER_PATH = 'mirror_user'
VAULT_DELETE_MIRROR_PATH = 'delete_mirror'
VAULT_SEND_EMAIL_PATH = 'send_email'
VAULT_SEND_SMS_PATH = 'send_sms'
VAULT_FETCH_SMS_PATH = 'fetch_sms'
VAULT_PASSWORD_RESET_PATH = 'password_reset'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'users.backends.TokenBackend',
)

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

TOKEN_TIMEOUT_DAYS = 1
SESSION_COOKIE_NAME = 'serafin_session'
SESSION_COOKIE_AGE = 60 * 60 * 24 # seconds


# Events

TRACK_AJAX_REQUESTS = False
TRACK_ANONYMOUS_USERS = True
TRACK_ADMIN_USERS = True


# Twilio

TWILIO_ACCOUNT_SID = 'xxxxx'
TWILIO_AUTH_TOKEN = 'xxxxx'


# Huey

HUEY = {
    'backend': 'huey.backends.redis_backend',
    'name': 'serafin',
    'connection': {
        'host': 'localhost',
        'port': 6379,
    },

    # Options to pass into the consumer when running `manage.py run_huey`
    'consumer_options': {
        'workers': 4,
        'utc': False,
    },
}


# REST Framework

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        'rest_framework.permissions.AllowAny',
    ]
}


# Admin interface

SUIT_CONFIG = {
    'ADMIN_NAME': 'Serafin admin',
    'HEADER_DATE_FORMAT': 'l j. F Y',

    'SEARCH_URL': '/admin/system/page/',

    'MENU': [
        {
            'app': 'users',
            'label': 'Brukere',
            'icon': 'icon-user',
            'models':
                [
                    'user',
                    'auth.groups',
                ]
        },
        {
            'app': 'system',
            'label': 'Program',
            'icon': 'icon-cog',
            'models':
                [
                    'program',
                    'part',
                    'page'
                ]
        },
        {
            'app': 'events',
            'label': 'Hendelser',
            'icon': 'icon-bullhorn',
            'models':
                [
                    'event',
                    'tasks.task',
                ]
        },
        {
            'app': 'filer',
            'label': 'Media',
            'icon': 'icon-picture'
        },
    ]
}

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'huey.log',
        },
    },
    'loggers': {
        'huey.consumer': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}


SOUTH_MIGRATION_MODULES = {
    'easy_thumbnails': 'easy_thumbnails.south_migrations',
}


try:
    from local_settings import *
except ImportError:
    pass
