from __future__ import unicode_literals

from django.http.response import HttpResponseForbidden
from tokens.tokens import token_generator
import json


def token_required(view_func):
    '''Decorator for views, checks that the user's token is valid.'''

    def _token_required(request, *args, **kwargs):
        data = json.loads(request.body)
        user_id = data.get('user_id')
        token = data.get('token')
        if user_id and token:
            if token_generator.check_token(user_id, token):
                return view_func(request, *args, **kwargs)

        return HttpResponseForbidden()

    return _token_required
