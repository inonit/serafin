from django.conf.urls import patterns, include, url
from events import receivers

urlpatterns = patterns('',
    url(r'^$', 'content.views.get_session', name='content'),
    url(r'^api/$', 'content.views.get_page', name='content_api'),
    url(r'^api/(?P<content_type>\w+)/(?P<file_id>\d+)$', 'content.views.api_filer_file', name='api_filer_file'),
    url(r'^(?P<route_slug>\w+)$', 'content.views.content_route', name='content_route'),
)
