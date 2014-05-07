from __future__ import unicode_literals

from tokens.json_status import STATUS_FAIL, STATUS_INVALID_TOKEN, STATUS_OK
from tokens.tokens import token_generator
from tokens.json_responses import JsonResponse
import json


def json_response(func):
    '''Handle JSON POST requests and respond in JSON'''

    def _json_response(request, *args, **kwargs):
        response = {
            'status': STATUS_FAIL,
        }
        if request.method == 'POST':
            data = json.loads(request.body)
            user_id = data.get('user_id')
            token = data.get('token')

            if user_id and token:
                if token_generator.check_token(user_id, token):
                    try:
                        func(request, user_id=user_id, data=data)
                        response['status'] = STATUS_OK
                    except:
                        pass # fail assumed above
                else:
                    response['status'] = STATUS_INVALID_TOKEN

        return JsonResponse(response)

    return _json_response
