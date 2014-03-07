from __future__ import unicode_literals
import json

from django.http import HttpResponse


class JsonResponse(HttpResponse):
    """ A json HTTP response class.
    """

    def __init__(self, content, content_type='application/json', status=200):
        super(HttpResponse, self).__init__(
            content=json.dumps(content),
            status=status,
            content_type=content_type,
        )
