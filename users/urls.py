from django.conf.urls import patterns, url
import users.views as views

urlpatterns = patterns('',
    url(r'^$', views.profile, name="users_profile"),
     url(r'^accounts/profile/$', views.profile, name="users_profile"),
    url(r'^accounts/login/$', views.login, name="users_login"),
    url(r'^accounts/logout/$', views.logout, name="users_logout"),
)