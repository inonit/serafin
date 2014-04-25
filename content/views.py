from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from filer.models import File, Image
import json


def get_page(request):

    response = {
        'status': 'ok',
    }

    return HttpResponse(json.dumps(response), content_type='application/json')


def api_filer_file(request, content_type=None, file_id=None):

    if content_type == 'image':
        filer_file = get_object_or_404(Image, id=file_id)
    else:
        filer_file = get_object_or_404(File, id=file_id)

    response = {
        'id': filer_file.id,
        'url': filer_file.url,
        'thumbnail': filer_file.icons['48'],
        'description': filer_file.original_filename,
    }

    return HttpResponse(json.dumps(response), content_type='application/json')
