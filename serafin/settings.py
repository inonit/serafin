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
SECRET_KEY = 'xxxxx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

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
    'south',
    'django_extensions',
    'django.contrib.admin',

    'tokens',
    'users',
    'vault',
    'tasker',
    'events',
    'content',
    'plumbing',
    'system',

    'rest_framework',
    'filer',
    'mptt',
    'easy_thumbnails',
    'huey.djhuey',
    'django_user_agents',
    'import_export',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'events.middleware.EventTrackingMiddleware',
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
    },
    'vault': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'vault.db'),
    }
}

DATABASE_ROUTERS = ['serafin.db_routers.VaultRouter']

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

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
    ('Admin', 'user@example.com'),
)
SERVER_EMAIL = 'Serafin <post@example.com>'
DEFAULT_FROM_EMAIL = 'Serafin <post@example.com>'
EMAIL_SUBJECT_PREFIX = '[Serafin] '
EMAIL_HOST_USER = 'xxxxx'
EMAIL_HOST_PASSWORD = 'xxxxx'
EMAIL_HOST = 'smtp.example.com'
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

LOG_AJAX_USER_DATA = True

LOG_REQUESTS = True
LOG_ANONYMOUS_REQUESTS = False
LOG_ADMIN_REQUESTS = False
LOG_AJAX_REQUESTS = False


# Twilio

TWILIO_ACCOUNT_SID = 'xxxxx'
TWILIO_AUTH_TOKEN = 'xxxxx'
TWILIO_FROM_NUMBER = '12345'


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

from django.utils.translation import ugettext_lazy as _

SUIT_CONFIG = {
    'CONFIRM_UNSAVED_CHANGES': False,
    'ADMIN_NAME': 'Serafin admin',
    'HEADER_DATE_FORMAT': 'l j. F Y',

    'SEARCH_URL': '/admin/system/page/',

    'MENU': [
        {
            'app': 'users',
            'label': _('Users'),
            'icon': 'icon-user',
            'models':
                [
                    'user',
                    'auth.group',
                ]
        },
        {
            'app': 'system',
            'label': _('Program'),
            'icon': 'icon-wrench',
            'models':
                [
                    'program',
                    'session',
                    'page',
                    'email',
                    'sms',
                    'variable',
                ]
        },
        {
            'app': 'events',
            'label': _('Events'),
            'icon': 'icon-bullhorn',
            'models':
                [
                    'event',
                    'tasker.task',
                ]
        },
        {
            'app': 'filer',
            'label': _('Media'),
            'icon': 'icon-picture'
        },
        {
            'app': 'sites',
            'label': _('Settings'),
            'icon': 'icon-cog'
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
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'huey_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'huey.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': [],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'huey.consumer': {
            'handlers': ['huey_log'],
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
