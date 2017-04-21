# coding: utf-8

SECRET_KEY = 'eis3seezaigei!j2ahYeen2pai2aesh3ye#M!aes'

USE_HTTPS = False

# E-mail settings

ADMINS = ()
SERVER_EMAIL = 'Serafin <post@example.com>'
DEFAULT_FROM_EMAIL = 'Serafin <post@example.com>'
EMAIL_SUBJECT_PREFIX = '[Serafin] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Twilio SMS backend (remove the ones you don't use)

# SMS_SERVICE = 'Twilio'
# TWILIO_ACCOUNT_SID = ''
# TWILIO_AUTH_TOKEN = ''
# TWILIO_FROM_NUMBER = ''

# Plivo SMS backend (remove the ones you don't use)

# SMS_SERVICE = 'Plivo'
# PLIVO_AUTH_ID = ''
# PLIVO_AUTH_TOKEN = ''
# PLIVO_FROM_NUMBER = ''

# Console SMS backend (remove the ones you don't use)

SMS_SERVICE = 'Console'

# Google Analytics

GOOGLE_ANALYTICS_ID = ''
