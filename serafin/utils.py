from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.http import HttpResponse
import json
import re


class JSONResponse(HttpResponse):
    def __init__(self, content):
        super(JSONResponse, self).__init__(
            content=json.dumps(content),
            content_type='application/json',
        )


def natural_join(listing):
    if len(listing) == 1:
        return listing[0]

    if len(listing) > 1:
        first = ', '.join(listing[:-1])
        last = listing[-1]
        return _('%(first)s and %(last)s') % locals()

    return ''


def user_data_replace(user, text):
    user_data = user.data

    markup = re.findall(r'{{.*?}}', text)
    for code in markup:

        variable = code[2:-2].strip()
        value = user_data.get(variable, '')
        if isinstance(value, list):
            value = natural_join(value)
        text = text.replace(code, unicode(value))

    return text


def process_session_links(user, text):
    '''Replaces session link markup with login link, activates session for given user'''

    from system.engine import Engine

    matches = re.findall(r'\[.*?\]\((session:(.*?))\)', text)
    for match in matches:
        session_str = match[0]
        session_id = match[1]

        init = {
            'current_session': session_id,
            'current_node': 0,
        }

        engine = Engine(user, init)
        engine.run()

        link = user.generate_login_link()
        text = text.replace(session_str, link)

    return text

