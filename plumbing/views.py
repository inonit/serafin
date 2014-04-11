from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from system.models import Page
import json


def api_page(request, page_id=None):

    page = get_object_or_404(Page, id=page_id)

    response = {
        'id': page.id,
        'title': page.title,
        'url': reverse('admin:system_page_change', args=[page.id]),
    }

    return HttpResponse(json.dumps(response), content_type='application/json')
