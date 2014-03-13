from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^(?P<user_id>\d+)/(?P<token>.+)/login/$', 'users.views.login_via_email',
        name='login_via_email'),
)
