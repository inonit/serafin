from django.conf.urls import include, url

from content.views import get_page, get_session, home, api_filer_file, content_route, \
    main_page, get_portal

urlpatterns = [
    url(r'^$', main_page, name='main_page'),
    url(r'^api/$', get_page, name='content_api'),
    url(r'api/v2.0/portal', get_portal, name='portal'),
    url(r'^api/(?P<content_type>\w+)/(?P<file_id>\d+)/$', api_filer_file, name='api_filer_file'),
    url(r'^home/$', home, name='home'),
    url(r'^session/$', get_session, name='content'),
    url(r'^(?P<route_slug>\w+)/$', content_route, name='content_route'),
]
