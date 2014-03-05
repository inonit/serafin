from __future__ import unicode_literals

from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout_then_login as django_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
import datetime

from logbook.users import djangologbookentry

@login_required()
def profile(request):
    djangologbookentry.debug(str(datetime.datetime.now()),'Loading user profile')
    template_name="profile.html"

    context = {
               'title': 'Welcome to your profile',
               }
    return render_to_response(
                              template_name,
                              context
                              )

def login(request, template_name="login.html"):
    """ Manual login to seraf """
    djangologbookentry.debug(str(datetime.datetime.now()),'Loading login page')
    return django_login(request, **{"template_name" : template_name})

def logout(request, template_name="login.html"):
    '''Manual Logout of seraf'''
    djangologbookentry.debug(str(datetime.datetime.now()),'User logging out')
    return django_logout(request)

