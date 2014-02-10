from django.http import HttpResponse
from models import VaultUser
import json


def json_response(func):
    '''Handles json POST requests and responds in json'''
    def _json_response(request, *args, **kwargs):
        response = {
            'status': 'failed',
        }

        if request.POST:
            data = json.reads(request.body)
            if 'user_id' in data and 'token' in data:
                try:
                    user = VaultUser.objects.get(id=data['user_id'])
                except VaultUser.DoesNotExist:
                    response['status'] = 'no such user'

                if not valid_token(data['token']):
                    response['status'] = 'bad authentication'

                response['status'] = func(request, user=user, data=data)

        return HttpResponse(json.dumps(response), 'application/json')


#@json_response
def send_email(request, *args, **kwargs):
    #return 'ok'
    return HttpResponse('', 'application/json')

#@json_response
def send_sms(request, *args, **kwargs):
    #return 'ok'
    return HttpResponse('', 'application/json')
