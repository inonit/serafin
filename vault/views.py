from __future__ import unicode_literals

from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from tokens.json_responses import JsonResponse
from tokens.tokens import token_generator
from vault.decorators import json_response
from vault.models import VaultUser
import json


@csrf_exempt
@json_response
def mirror_user(request, *args, **kwargs):
    '''Store user sensitive information to vault'''

    vault_user, created = VaultUser.objects.get_or_create(id=kwargs['user_id'])

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

    vault_user = VaultUser.objects.get(id=kwargs['user_id'])

    if vault_user:
        vault_user.delete()


@csrf_exempt
@json_response
def send_email(request, *args, **kwargs):
    '''Send email to vault user'''

    vault_user = VaultUser.objects.get(id=kwargs['user_id'])

    data = kwargs.get('data')
    subject = data.get('subject')
    message = data.get('message')
    html_message = data.get('html_message')

    if vault_user:
        vault_user.send_email(subject, message, html_message)


@csrf_exempt
@json_response
def send_sms(request, *args, **kwargs):
    '''Send sms to vault user'''

    vault_user = VaultUser.objects.get(id=kwargs['user_id'])

    data = kwargs.get('data')
    message = data.get('message')

    if vault_user and message:
        vault_user.send_sms(message=message)


@csrf_exempt
@json_response
def fetch_sms(request, *args, **kwargs):
    '''Fetch sms response from user'''
    pass


@csrf_exempt
def password_reset(request, *args, **kwargs):
    '''Send password reset email'''

    vault_user = VaultUser.objects.get(email__iexact=data.get('email'))

    data = json.loads(request.body)

    protocol = data.get('protocol')
    domain = data.get('domain')
    path = data.get('path')
    site_name = data.get('site_name')

    if vault_user and protocol and domain and path and site_name:

        link = '%(protocol)s://%(domain)s%(path)s%(uid)s/%(token)s' % {
            'protocol': protocol,
            'domain': domain,
            'path': path,
            'uid': urlsafe_base64_encode(force_bytes(vault_user.id)),
            'token': token_generator.make_token(vault_user.id),
        }

        subject_template = get_template('registration/password_reset_subject.txt')
        content_template = get_template('registration/password_reset_email.html')

        context = {
            'site_name': site_name,
            'link': link,
            'user': vault_user,
        }

        subject = subject_template.render(Context({'site_name': site_name}))
        subject = ''.join(subject.splitlines())
        content = content_template.render(Context(context))

        if subject and content:
            vault_user.send_email(subject, content)

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'bad data'})
