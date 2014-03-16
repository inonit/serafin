from __future__ import unicode_literals

from django.conf.urls import patterns, url
import users.views as views

urlpatterns = patterns('',
    url(r'^accounts/login$', views.login, name='users_login'),
    url(r'^accounts/logout$', views.logout, name='users_logout'),
    url(r'^(?P<user_id>\d+)/(?P<token>.+)/login$', 'users.views.login_via_email',
        name='login_via_email'),
)
