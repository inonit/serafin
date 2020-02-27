from __future__ import unicode_literals

from django.conf.urls import url
from users.forms import PasswordResetForm
from tokens.tokens import token_generator

from django.contrib.auth import views as auth_views
from users.views import manual_login, manual_logout, login_via_email, profile, receive_sms

urlpatterns = [
    url(r'^login/$', manual_login, name='login'),
    url(r'^logout/$', manual_logout, name='logout'),
    url(r'^login/(?P<user_id>\d+)/(?P<token>.+)$',
        login_via_email,
        name='login_via_email'
        ),
    url(r'^recover_password/$', auth_views.PasswordResetView.as_view(), {
        'post_reset_redirect': '/recover_password/sent/',
        'password_reset_form': PasswordResetForm,
    },
        name='password_reset'
        ),
    url(r'^recover_password/sent/$', auth_views.PasswordResetDoneView.as_view()),
    url(r'^recover_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$',
        auth_views.PasswordResetConfirmView.as_view(), {
            'post_reset_redirect': '/recover_password/done/',
            'token_generator': token_generator,
        },
        name='password_reset_confirm'
        ),
    url(r'^recover_password/done/$', auth_views.PasswordResetCompleteView.as_view()),
    url(r'^profile/$', profile, name='profile'),
    url(r'^api/users/receive_sms$', receive_sms, name='receive_sms')
]
