from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('users.urls')),
    url(r'^', include('content.urls')),

    url(r'^api/vault/', include('vault.urls')),
    url(r'^api/plumbing/', include('plumbing.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
