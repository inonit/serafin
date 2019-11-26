from __future__ import unicode_literals

from django.conf.urls import url
from users.forms import PasswordResetForm
from tokens.tokens import token_generator

from django.contrib.auth.views import password_reset, password_reset_done, \
    password_reset_confirm, password_reset_complete
from users.views import manual_login, manual_logout, login_via_email, profile, receive_sms

urlpatterns = [
    url(r'^login/$', manual_login, name='login'),
    url(r'^logout/$', manual_logout, name='logout'),
    url(r'^login/(?P<user_id>\d+)/(?P<token>.+)$',
        login_via_email,
        name='login_via_email'
    ),
    url(r'^recover_password/$', password_reset, {
            'post_reset_redirect': '/recover_password/sent/',
            'password_reset_form': PasswordResetForm,
        },
        name='password_reset'
    ),
    url(r'^recover_password/sent/$', password_reset_done),
    url(r'^recover_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$',
            password_reset_confirm, {
            'post_reset_redirect': '/recover_password/done/',
            'token_generator': token_generator,
        },
        name='password_reset_confirm'
    ),
    url(r'^recover_password/done/$', password_reset_complete),
    url(r'^profile/$', profile, name='profile'),
    url(r'^api/users/receive_sms$', receive_sms, name='receive_sms'),
]
