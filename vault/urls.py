from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<user_id>\d.+)/(?P<token>.+)/send_email/$', 'vault.views.send_email', name='send_email'),
    url(r'^(?P<user_id>\d.+)/(?P<token>.+)/send_sms/$', 'vault.views.send_sms', name='send_sms'),
)
