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

