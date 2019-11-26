from __future__ import unicode_literals

from django.conf.urls import url
from plumbing.views import api_node

urlpatterns = [
    url(r'^$', api_node, name='api_node'),
    url(r'^(?P<node_type>\w+)/$', api_node, name='api_node'),
    url(r'^(?P<node_type>\w+)/(?P<node_id>\d+)$', api_node, name='api_node'),
]
