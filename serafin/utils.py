from __future__ import unicode_literals

from django.http import HttpResponse
import json
import re


class JSONResponse(HttpResponse):
    def __init__(self, content):
        super(JSONResponse, self).__init__(
            content=json.dumps(content),
            content_type='application/json',
        )


def user_data_replace(user, text):
    user_data = user.data

    markup = re.findall(r'{{.*?}}', text)
    for code in markup:

        variable = code[2:-2].strip()
        value = user_data.get(variable, '')
        text = text.replace(code, unicode(value))

    return text

