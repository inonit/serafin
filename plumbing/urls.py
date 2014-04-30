from __future__ import unicode_literals

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'plumbing.views.api_node', name='api_node'),
    url(r'^(?P<node_type>\w+)/$', 'plumbing.views.api_node', name='api_node'),
    url(r'^(?P<node_type>\w+)/(?P<node_id>\d+)$', 'plumbing.views.api_node', name='api_node'),
)
