from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import logout_then_login as django_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from django.shortcuts import render
from users.models import User, UserField

@login_required()
def profile(request):
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
    return django_login(request, **{"template_name" : template_name})

def logout(request, template_name="login.html"):
    '''Manual Logout of seraf'''
    return django_logout(request)

