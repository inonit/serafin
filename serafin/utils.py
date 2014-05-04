from __future__ import unicode_literals

from django.http import HttpResponse
import json


class JSONResponse(HttpResponse):
    def __init__(self, content):
        super(JSONResponse, self).__init__(
            content=json.dumps(content),
            content_type='application/json',
        )
