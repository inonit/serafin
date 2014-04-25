from __future__ import unicode_literals

from vault.decorators import json_response
from vault.models import VaultUser


@json_response
def mirror_user(request, *args, **kwargs):
    '''Store user sensitive information to vault'''

    data = kwargs.get('data')

    email = data.get('email')
    phone = data.get('phone')

    user_id = kwargs.get('user_id')

    try:
        vault_user = VaultUser.objects.get(id=user_id)
    except VaultUser.DoesNotExist:
        vault_user = VaultUser(
            id=user_id
        )

    vault_user.email = email
    vault_user.phone = phone
    vault_user.save()


@json_response
def delete_mirror(request, *args, **kwargs):
    '''Remove user associated sensitive information from vault'''

    vault_user = kwargs.get('user')
    if vault_user:
        vault_user.delete()


@json_response
def send_email(request, *args, **kwargs):
    '''Send email to vault user'''

    data = kwargs.get('data')

    subject = data.get('subject', None)
    message = data.get('message', None)
    html_message = data.get('html_message', None)

    vault_user = kwargs.get('user')
    vault_user.send_email(subject, message, html_message)


@json_response
def send_sms(request, *args, **kwargs):
    '''Send sms to vault user'''
    return


@json_response
def fetch_sms(request, *args, **kwargs):
    '''Send email to vault user'''
    return
