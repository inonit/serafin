from .decorators import json_response


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


@json_response
def send_email(request, *args, **kwargs):
    """ Sends email to vault user """

    data = kwargs.get('data')

    subject = data.get('subject', None)
    message = data.get('message', None)
    html_message = data.get('html_message', None)

    vault_user = kwargs.get('user')
    vault_user.send_email(subject, message, html_message)

    return


#@json_response
def send_sms(request, *args, **kwargs):
    return


#@json_response
def fetch_sms(request, *args, **kwargs):
    return
