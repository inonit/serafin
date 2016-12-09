'''Test settings and globals which allow us to run our test suite locally.'''
from serafin.settings import *

# Test settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = BASE_DIR
TEST_DISCOVER_ROOT = BASE_DIR
TEST_DISCOVER_PATTERN = 'test_*'

# In-memory test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

HUEY.update({'always_eager': True})
