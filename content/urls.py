from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^part/(?P<part_id>\d+)$', 'content.views.part', name='part'),
    url(r'^page/(?P<page_id>\d+)$', 'content.views.page', name='page'),
    url(r'^design$', 'content.views.design', name='design'),
)
