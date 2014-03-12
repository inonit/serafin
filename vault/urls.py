from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^(?P<user_id>\d+)/(?P<token>.+)/mirror_user/$', 'vault.views.mirror_user', name='mirror_user'),
    url(r'^(?P<user_id>\d+)/(?P<token>.+)/delete_mirror/$', 'vault.views.delete_mirror', name='delete_mirror'),
    url(r'^(?P<user_id>\d+)/(?P<token>.+)/send_email/$', 'vault.views.send_email', name='send_email'),
    url(r'^(?P<user_id>\d+)/(?P<token>.+)/send_sms/$', 'vault.views.send_sms', name='send_sms'),
    url(r'^(?P<user_id>\d+)/(?P<token>.+)/fetch_sms/$', 'vault.views.fetch_sms', name='fetch_sms'),
)
