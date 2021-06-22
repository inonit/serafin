import re

from django.conf import settings
from django.conf.urls import include, url, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic.base import RedirectView

from system.views import export_text, import_text, set_program, set_stylesheet, redirect_media

admin.autodiscover()

favicon_view = RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.ico', permanent=True)


def not_found_error(request, exception=None):
    return render(request, 'page_not_found_error.html', status=404)


handler404 = not_found_error

urlpatterns = [
    url(r'^api/plumbing/', include('plumbing.urls')),
    url(r'^api/system/', include('system.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^admin/defender/', include('defender.urls')),
    url(r'^admin/export_text/', export_text),
    url(r'^admin/import_text/', import_text),
    url(r'^admin/set_program/$', set_program, name="set_program"),
    url(r'^admin/set_stylesheet/$', set_stylesheet, name="set_stylesheet"),
    url('i18n/', include('django.conf.urls.i18n')),

    url(r'^healthz$', lambda r: HttpResponse()),

    url(r'^', include('users.urls')),
    url(r'^', include('content.urls')),
    re_path(r'^favicon\.ico$', favicon_view),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [url(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')), redirect_media)]
