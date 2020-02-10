from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'content.views.get_session', name='content'),
    url(r'^get_location_from_ip/$', 'content.views.get_location_from_ip', name='get_location_from_ip'),
    url(r'^api/$', 'content.views.get_page', name='content_api'),
    url(r'^api/(?P<content_type>\w+)/(?P<file_id>\d+)/$', 'content.views.api_filer_file', name='api_filer_file'),
    url(r'^home/$', 'content.views.home', name='home'),
    url(r'^(?P<route_slug>\w+)/$', 'content.views.content_route', name='content_route'),
)
