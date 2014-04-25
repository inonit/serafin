from __future__ import unicode_literals

from tokens.json_status import STATUS_FAIL, STATUS_USER_DOES_NOT_EXIST, STATUS_INVALID_TOKEN, STATUS_OK
from tokens.tokens import token_generator
from tokens.json_responses import JsonResponse
from vault.models import VaultUser


def json_response(func):
    '''Handle JSON POST requests and respond in JSON'''

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
                    except:
                        pass
                else:
                    response['status'] = STATUS_INVALID_TOKEN
        return JsonResponse(response)

    return _json_response