from __future__ import unicode_literals
from .decorators import json_response
from .models import VaultUser


@json_response
def mirror_user(request, *args, **kwargs):
    """ Store user sensitive information to vault """

    data = kwargs.get('data')

    email = data.get('email')
    phone = data.get('phone')

    user_id = kwargs.get('user_id')
    vault_user = kwargs.get('user')

    if not vault_user:
        try:
            vault_user = VaultUser.objects.get(id=user_id)
        except VaultUser.DoesNotExist:
            vault_user = VaultUser(
                id=user_id
            )

    vault_user.email = email
    vault_user.phone = phone
    vault_user.save()

    return


@json_response
def delete_mirror(request, *args, **kwargs):
    """ Removes user associated sensitive information from vault """

    vault_user = kwargs.get('user')
    if vault_user:
        vault_user.delete()

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
