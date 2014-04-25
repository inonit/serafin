from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^login$', 'users.views.manual_login', name='login'),
    url(r'^logout$', 'users.views.manual_logout', name='logout'),
    url(r'^login/(?P<user_id>\d+)/(?P<token>.+)$', 'users.views.login_via_email',
        name='login_via_email'),
)
