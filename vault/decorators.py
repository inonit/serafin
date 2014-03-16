from __future__ import unicode_literals
from token_auth.json_status import STATUS_FAIL, STATUS_USER_DOES_NOT_EXIST, STATUS_INVALID_TOKEN, STATUS_OK

from token_auth.tokens import token_generator
from token_auth.json_responses import JsonResponse
from .models import VaultUser


def json_response(func):
    """ Handles json POST requests and responds in json """

    def _json_response(request, *args, **kwargs):
        response = {
            'status': STATUS_FAIL,
        }
        if request.POST:
            data = request.POST
            user_id = data.get('user_id')
            token = data.get('token')

            if user_id and token:
                try:
                    user = VaultUser.objects.get(id=user_id)
                except VaultUser.DoesNotExist:
                    user = None
                    response['status'] = STATUS_USER_DOES_NOT_EXIST

                if token_generator.check_token(user_id, token):
                    try:
                        func(request, user=user, user_id=user_id, data=data)
                        response['status'] = STATUS_OK
                    except Exception, e:
                        pass
                else:
                    response['status'] = STATUS_INVALID_TOKEN
        return JsonResponse(response)

    return _json_response