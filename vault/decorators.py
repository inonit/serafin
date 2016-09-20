from __future__ import unicode_literals

from django.http import JsonResponse

from tokens.json_status import STATUS_FAIL, STATUS_INVALID_TOKEN, STATUS_OK
from tokens.tokens import token_generator
import json


def json_response(func):
    '''Handle JSON POST requests and respond in JSON'''

    def _json_response(request, *args, **kwargs):

        response = {'status': 'Fail.'}

        if request.method == 'POST':

            data = json.loads(request.body)
            user_id = data.get('user_id')
            token = data.get('token')

            if user_id and token:
                if token_generator.check_token(user_id, token):
                    try:
                        response = func(request, user_id=user_id, data=data)
                        if not response:
                            response = {'status': 'OK'}
                    except:
                        pass # fail assumed above

        return JsonResponse(response)

    return _json_response
