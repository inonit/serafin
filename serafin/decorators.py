from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from functools import wraps


def in_session(redirect_url):
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            if None == request.user.data.get('current_session', None):
                return HttpResponseRedirect(redirect_url)
            else:
                return func(request, *args, **kwargs)
        return wraps(func)(inner_decorator)

    return decorator