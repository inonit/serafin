from __future__ import unicode_literals

from django.conf.urls import patterns, url
from users.forms import PasswordResetForm
from tokens.tokens import token_generator


urlpatterns = patterns('',
    url(r'^login/$', 'users.views.manual_login', name='login'),
    url(r'^logout/$', 'users.views.manual_logout', name='logout'),
    url(r'^login/(?P<user_id>\d+)/(?P<token>.+)$',
        'users.views.login_via_email',
        name='login_via_email'
    ),
    url(r'^recover_password/$', 'django.contrib.auth.views.password_reset', {
            'post_reset_redirect': '/recover_password/sent/',
            'password_reset_form': PasswordResetForm,
        },
        name='password_reset'
    ),
    url(r'^recover_password/sent/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^recover_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$',
        'django.contrib.auth.views.password_reset_confirm', {
            'post_reset_redirect': '/recover_password/done/',
            'token_generator': token_generator,
        },
        name='password_reset_confirm'
    ),
    url(r'^recover_password/done/$',
        'django.contrib.auth.views.password_reset_complete'
    ),
    url(r'^profile/$', 'users.views.profile', name='profile'),
    url(r'^api/users/receive_sms$', 'users.views.receive_sms', name='receive_sms'),
)
