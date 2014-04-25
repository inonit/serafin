from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^users/(?P<user_id>\d+)/mirror_user/$', 'vault.views.mirror_user', name='mirror_user'),
    url(r'^users/(?P<user_id>\d+)/delete_mirror/$', 'vault.views.delete_mirror', name='delete_mirror'),
    url(r'^users/(?P<user_id>\d+)/send_email/$', 'vault.views.send_email', name='send_email'),
    url(r'^users/(?P<user_id>\d+)/send_sms/$', 'vault.views.send_sms', name='send_sms'),
    url(r'^users/(?P<user_id>\d+)/fetch_sms/$', 'vault.views.fetch_sms', name='fetch_sms'),
)
