from __future__ import unicode_literals

import json
import requests
from django.conf import settings
from tokens.json_status import STATUS_OK


def vault_post(func):
    '''Helper decorator for posting JSON requests to Vault'''

    def _vault_post(*args, **kwargs):

        path, user_id, token = func(*args, **kwargs)

        if path and user_id and token:
            data = {
                'user_id': user_id,
                'token': token,
            }
            data.update(kwargs)

            url = '%(server_url)s%(path)s' % {
                'server_url': settings.VAULT_SERVER_API_URL,
                'path': path
            }

            headers = {
                'content-type': 'application/json',
            }

            response = requests.post(url, data=json.dumps(data), headers=headers)
            response.raise_for_status()

            return response.json()

        return False

    return _vault_post
