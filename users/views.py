from __future__ import unicode_literals

from django.contrib.auth import login, authenticate
from django.http.response import HttpResponse


def login_via_email(request, user_id, token):
    """ Authenticates a user via e-mailed link
    """

    user = authenticate(user_id=user_id, token=token)
    if user:
        login(request, user)
        #TODO: redirect to day's program page
        return HttpResponse('Logged in')

    #TODO: redirect to invalid token page
    return HttpResponse('Not Logged')