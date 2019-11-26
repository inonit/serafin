from django.conf.urls import include, url

from content.views import get_page, get_session, home, api_filer_file, content_route

urlpatterns = [
    url(r'^$', get_session, name='content'),
    url(r'^api/$', get_page, name='content_api'),
    url(r'^api/(?P<content_type>\w+)/(?P<file_id>\d+)/$', api_filer_file, name='api_filer_file'),
    url(r'^home/$', home, name='home'),
    url(r'^(?P<route_slug>\w+)/$', content_route, name='content_route'),
]
