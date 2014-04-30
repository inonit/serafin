from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from system.models import Page
from content.models import Email, SMS
import json


def api_node(request, node_type=None, node_id=None):

    if node_type == 'page':
        node = get_object_or_404(Page, id=node_id)
        url = reverse('admin:system_page_change', args=[node.id])
    if node_type == 'email':
        node = get_object_or_404(Email, id=node_id)
        url = reverse('admin:content_email_change', args=[node.id])
    if node_type == 'sms':
        node = get_object_or_404(SMS, id=node_id)
        url = reverse('admin:content_sms_change', args=[node.id])

    response = {
        'id': node.id,
        'title': node.title,
        'url': url,
    }

    return HttpResponse(json.dumps(response), content_type='application/json')
