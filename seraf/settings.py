"""
Django settings for seraf project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

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

ALLOWED_HOSTS = ['seraf.inonit.no']


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'suit',
    'django.contrib.admin',

    'south',
    'django_extensions',
    'filer',
    'mptt',
    'easy_thumbnails',
    'mail_templated',

    'users',
    'vault',
    'sms',
    'tasks',
    'events',
    'content',
    'system',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'seraf.urls'

WSGI_APPLICATION = 'seraf.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'seraf.db'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'nb'

TIME_ZONE = 'Europe/Oslo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


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


# User model and vault separation

AUTH_USER_MODEL = 'users.User'

VAULT_MIRROR_USER = '/api/vault/mirror_user'
VAULT_DELETE_MIRROR = '/api/vault/delete_mirror'
VAULT_SEND_EMAIL_URL = '/api/vault/send_email'
VAULT_SEND_SMS_URL = '/api/vault/send_sms'
VAULT_FETCH_SMS_URL = '/api/vault/fetch_sms'


# Twilio

TWILIO_ACCOUNT_SID = 'xxxxx'
TWILIO_AUTH_TOKEN = 'xxxxx'


# Huey

HUEY = {
    'backend': 'huey.backends.redis_backend',
    'name': 'seraf',
    'connection': {
        'host': 'localhost',
        'port': 6379,
    },

    # Options to pass into the consumer when running `manage.py run_huey`
    'consumer_options': {
        'workers': 4,
    },
}


# Admin interface

SUIT_CONFIG = {
    'ADMIN_NAME': 'SERAF admin',
    'HEADER_DATE_FORMAT': 'l j. F Y',

    #'SEARCH_URL': '/admin/',

    'MENU_ICONS': {

    },
}

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)


try:
    from local_settings import *
except ImportError:
    pass
