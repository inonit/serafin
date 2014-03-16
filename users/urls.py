from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^accounts/login$', 'users.views.login', name='login'),
    url(r'^accounts/logout$', 'users.views.logout', name='logout'),
    url(r'^(?P<user_id>\d+)/(?P<token>.+)/login$', 'users.views.login_via_email',
        name='login_via_email'),
)
