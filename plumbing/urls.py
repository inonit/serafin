from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^page/$', 'plumbing.views.api_page', name='api_page'),
    url(r'^page/(?P<page_id>\d+)$', 'plumbing.views.api_page', name='api_page'),
)
