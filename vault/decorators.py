from __future__ import unicode_literals
from django.contrib.auth import authenticate

from django.http.response import HttpResponseForbidden

from vault.models import VaultUser


def token_required(view_func):
    """ Decorator for views that checks that the user's token
    is valid.
    """

    def wrap(request, *args, **kwargs):
        user_id = request.REQUEST.get('user_id')
        token = request.REQUEST.get('token')
        if user_id and token:
            user = authenticate(pk=user_id, token=token)
            if user:
                try:
                    VaultUser.objects.get(id=user_id)
                except VaultUser.DoesNotExist:
                    return HttpResponseForbidden()

                return view_func(request, *args, **kwargs)

        return HttpResponseForbidden()

    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap