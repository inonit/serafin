from django.http import HttpResponse
from django.utils import json
from models import VaultUser


def send_email(request, user_id=None, token=None):
    response = {
        'status': 'ok',
    }
    if user_id and token:
        try:
            user = VaultUser.objects.get(id=user_id)
        except VaultUser.DoesNotExist:
            response['status'] = 'no such user'

        try:
            data = json.loads(request.POST['data'])
        except:
            response['status'] = 'bad data'

    return HttpResponse(json.dumps(response), 'application/json')



def send_sms(request, user_id=None, token=None):
    response = {
        'status': 'ok',
    }
    if user_id and token:
        try:
            user = VaultUser.objects.get(id=user_id)
        except VaultUser.DoesNotExist:
            response['status'] = 'no such user'

        try:
            data = json.loads(request.POST['data'])
        except:
            response['status'] = 'bad data'

    return HttpResponse(json.dumps(response), 'application/json')

