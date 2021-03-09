from __future__ import unicode_literals

from django.conf.urls import url
from users.forms import PasswordResetForm, CustomSetPasswordForm
from tokens.tokens import token_generator

from django.contrib.auth import views as auth_views
from users.views import manual_login, manual_logout, login_via_email, profile, receive_sms, CustomPasswordChangeView

urlpatterns = [
    url(r'^login/$', manual_login, name='login'),
    url(r'^logout/$', manual_logout, name='logout'),
    url(r'^login/(?P<user_id>\d+)/(?P<token>.+)$',
        login_via_email,
        name='login_via_email'
        ),
    url(r'^recover_password/$', auth_views.PasswordResetView.as_view(form_class=PasswordResetForm),
        name='password_reset'),
    url(r'^recover_password/sent/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^recover_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$',
        auth_views.PasswordResetConfirmView.as_view(token_generator=token_generator, form_class=CustomSetPasswordForm), name='password_reset_confirm'),
    url(r'^recover_password/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^api/users/receive_sms$', receive_sms, name='receive_sms'),
    url(r'^password_change/$', CustomPasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    url(r'^password_change/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done')
]
