from __future__ import unicode_literals
import json
from django.conf import settings

import requests
from tokens.json_status import STATUS_OK


def vault_post(func):
    '''
    Helper decorator for posting JSON requests to Vault
    '''

    def _vault_post(*args, **kwargs):

        url, user_id, token = func(*args, **kwargs)

        if url and user_id and token:
            data = {
                'user_id': user_id,
                'token': token,
            }
            data.update(kwargs)

            url = '%(server_url)s%(user_id)s/%(token)s/%(api_handler)s' % {
                'server_url': settings.VAULT_SERVER_API_URL,
                'user_id': user_id,
                'token': token,
                'api_handler': url
            }
            response = requests.post(url, data=json.dumps(data))
            response.raise_for_status()

            response_json = response.json()
            status = response_json.get('status')
            if status and status == STATUS_OK:
                return True

        return False

    _vault_post.__doc__ = func.__doc__
    _vault_post.__dict__ = func.__dict__
    return _vault_post
