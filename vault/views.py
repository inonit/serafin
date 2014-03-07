from django.http import HttpResponse
from models import VaultUser


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
