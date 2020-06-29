from django.conf.urls import include, url
from django.urls import path
from content.views import get_page, get_session, home, api_filer_file, content_route, \
    main_page, get_portal, modules_page, module_redirect, therapist_zone, users_stats, \
    tools_page, chat, my_therapist

urlpatterns = [
    path('', main_page, name='main_page'),
    path('modules/', modules_page, name='modules'),
    path('module/<int:module_id>/', module_redirect, name='module'),
    path('tools/', tools_page, name='tools' ),
    path('api/', get_page, name='content_api'),
    path('api/v2.0/portal', get_portal, name='portal'),
    path('api/<str:content_type>/<int:file_id>/', api_filer_file, name='api_filer_file'),
    path('home/', home, name='home'),
    path('therapist/', therapist_zone, name='therapist_zone'),
    path('api/v2.0/users_stats', users_stats, name='users_stats'),
    path('mytherapist/', my_therapist, name='mytherapist'),
    path('api/v1.0/chat', chat, name='chat'),
    path('session/<int:module_id>/', get_session, name='content'),
    path('session/', get_session, name='content'),
    path('<str:route_slug>/', content_route, name='content_route'),
]
