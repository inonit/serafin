from __future__ import unicode_literals

from vault.decorators import json_response
from vault.models import VaultUser

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@json_response
def mirror_user(request, *args, **kwargs):
    '''Store user sensitive information to vault'''

    vault_user = kwargs.get('user')

    if not vault_user:
        vault_user = VaultUser(id=kwargs.get('user_id'))

    data = kwargs.get('data')
    email = data.get('email')
    phone = data.get('phone')

    if email and phone:
        vault_user.email = email
        vault_user.phone = phone

    vault_user.save()


@csrf_exempt
@json_response
def delete_mirror(request, *args, **kwargs):
    '''Remove user associated sensitive information from vault'''

    vault_user = kwargs.get('user')

    if vault_user:
        vault_user.delete()


@csrf_exempt
@json_response
def send_email(request, *args, **kwargs):
    '''Send email to vault user'''

    data = kwargs.get('data')

    subject = data.get('subject')
    message = data.get('message')
    html_message = data.get('html_message')

    vault_user = kwargs.get('user')

    if vault_user:
        vault_user.send_email(subject, message, html_message)


@csrf_exempt
@json_response
def send_sms(request, *args, **kwargs):
    '''Send sms to vault user'''

    vault_user = kwargs.get('user')
    message = kwargs.get('data').get('message')

    if vault_user and message:
        vault_user.send_sms(message=message)


@csrf_exempt
@json_response
def fetch_sms(request, *args, **kwargs):
    '''Fetch sms response from user'''
    pass
