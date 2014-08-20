from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('vault.views',
    url(r'^mirror_user$', 'mirror_user', name='mirror_user'),
    url(r'^delete_mirror$', 'delete_mirror', name='delete_mirror'),
    url(r'^send_email$', 'send_email', name='send_email'),
    url(r'^send_sms$', 'send_sms', name='send_sms'),
    url(r'^receive_sms$', 'receive_sms', name='receive_sms'),
    url(r'^password_reset$', 'password_reset', name='vault_password_reset'),
)
