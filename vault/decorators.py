from __future__ import unicode_literals
import json
from token_auth.json_status import STATUS_FAIL, STATUS_USER_DOES_NOT_EXIST, STATUS_INVALID_TOKEN, STATUS_OK

from token_auth.tokens import token_generator
from token_auth.json_responses import JsonResponse
from vault.models import VaultUser


def json_response(func):
    """ Handles json POST requests and responds in json """

    def _json_response(request, *args, **kwargs):
        response = {
            'status': STATUS_FAIL,
        }

        if request.POST:
            data = json.reads(request.body)
            user_id = data.get('user_id')
            token = data.get('token')

            if user_id and token:
                try:
                    user = VaultUser.objects.get(id=user_id)
                except VaultUser.DoesNotExist:
                    response['status'] = STATUS_USER_DOES_NOT_EXIST

                if not token_generator.check_token(token):
                    response['status'] = STATUS_INVALID_TOKEN

                response['status'] = STATUS_OK

                response = func(request, user=user, data=data, response=response)

        return JsonResponse(response)