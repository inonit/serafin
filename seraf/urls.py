from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'seraf.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include('content.urls')),

    url(r'^api/vault/', include('vault.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
