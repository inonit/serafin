from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^mirror_user$', 'vault.views.mirror_user', name='mirror_user'),
    url(r'^delete_mirror$', 'vault.views.delete_mirror', name='delete_mirror'),
    url(r'^send_email$', 'vault.views.send_email', name='send_email'),
    url(r'^send_sms$', 'vault.views.send_sms', name='send_sms'),
    url(r'^fetch_sms$', 'vault.views.fetch_sms', name='fetch_sms'),
)
