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

                response = func(request, user=user, data=data, response=response)

        return HttpResponse(json.dumps(response), 'application/json')


#@json_response
def mirror_user(request, *args, **kwargs):
    #try:
        #user = VaultUser.objects.get_or_create(id=kwargs['user'])
        #user.email = kwargs['data']['email']
        #user.phone = kwargs['data']['phone']
        #user.save()
    #except:
        #return 'not saved'
    return

#@json_response
def delete_mirror(request, *args, **kwargs):
    #try:
        #VaultUser.objects.get(id=kwargs['user']).delete()
    #except:
        #return 'no such user'
    return

#@json_response
def send_email(request, *args, **kwargs):
    return

#@json_response
def send_sms(request, *args, **kwargs):
    return

#@json_response
def fetch_sms(request, *args, **kwargs):
    return
