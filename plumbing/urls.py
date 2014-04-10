from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^get$', 'plumbing.views.plumbing_get', name='plumbing_get'),
    url(r'^post$', 'plumbing.views.plumbing_post', name='plumbing_post'),
)
