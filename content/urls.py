from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'content.views.page_test', name='page_test'),
)
