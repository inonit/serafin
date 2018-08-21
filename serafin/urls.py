import re

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.http.response import HttpResponse

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/plumbing/', include('plumbing.urls')),
    url(r'^api/system/', include('system.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/export_text/', 'system.views.export_text'),
    url(r'^admin/import_text/', 'system.views.import_text'),
    url(r'^admin/set_program/$', 'system.views.set_program', name="set_program"),
    url(r'^admin/set_stylesheet/$', 'system.views.set_stylesheet', name="set_stylesheet"),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^healthz$', lambda r: HttpResponse()),

    url(r'^', include('users.urls')),
    url(r'^', include('content.urls')),
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [url(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')), 'system.views.redirect_media')]
