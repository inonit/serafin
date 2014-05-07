from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import login, logout, authenticate
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.views import login as django_login


def manual_login(request):
    if request.user.is_authenticated():
        return redirect('/')
    return django_login(request, template_name='login.html')


def manual_logout(request):
    if request.user.is_authenticated():
        logout(request.user)
    return redirect('/')


def login_via_email(request, user_id=None, token=None):

    user = authenticate(user_id=user_id, token=token)
    if user:
        login(request, user)
        return redirect('/')

    return redirect('login')
