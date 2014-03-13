from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import login, authenticate
from django.http.response import HttpResponse
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout_then_login as django_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required()
def profile(request):
    template_name = 'profile.html'

    context = {
        'title': _('Welcome to your profile'),
    }
    return render(request, template_name, context)


def login(request, template_name='login.html'):
    '''Manual login to SERAF'''
    return django_login(request, **{'template_name' : template_name})


def logout(request, template_name='login.html'):
    '''Manual logout of SERAF'''
    return django_logout(request)


def login_via_email(request, user_id, token):
    '''Authenticates a user via e-mailed link'''

    user = authenticate(user_id=user_id, token=token)
    if user:
        login(request, user)
        #TODO: redirect to day's program page
        return HttpResponse(_('Logged in'))

    #TODO: redirect to invalid token page
    return HttpResponse(_('Not logged in'))
