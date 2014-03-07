from __future__ import unicode_literals

from django.http.response import HttpResponseForbidden

from token_auth.tokens import token_generator


def token_required(view_func):
    """ Decorator for views that checks that the user's token
    is valid.
    """

    def wrap(request, *args, **kwargs):
        user_id = request.REQUEST.get('user_id')
        token = request.REQUEST.get('token')
        if user_id and token:
            if token_generator.check_token(token):
                return view_func(request, *args, **kwargs)

        return HttpResponseForbidden()

    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap