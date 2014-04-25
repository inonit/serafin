from __future__ import unicode_literals

from django.http.response import HttpResponseForbidden
from tokens.tokens import token_generator


def token_required(view_func):
    '''Decorator for views, checks that the user's token is valid.'''

    def _token_required(request, *args, **kwargs):
        user_id = request.REQUEST.get('user_id')
        token = request.REQUEST.get('token')
        if user_id and token:
            if token_generator.check_token(user_id, token):
                return view_func(request, *args, **kwargs)

        return HttpResponseForbidden()

    _token_required.__doc__ = view_func.__doc__
    _token_required.__dict__ = view_func.__dict__
    return _token_required
