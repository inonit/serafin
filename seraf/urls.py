from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from system.models import Part, Page
from rest_framework import viewsets, routers


class PartViewSet(viewsets.ModelViewSet):
    model = Part


class PageViewSet(viewsets.ModelViewSet):
    model = Page


router = routers.DefaultRouter()
router.register(r'api/parts', PartViewSet)
router.register(r'api/pages', PageViewSet)


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'seraf.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include('content.urls')),

    url(r'^api/vault/', include('vault.urls')),

    url(r'^', include(router.urls)),
    url(r'^api/plumbing/', include('plumbing.urls')),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
