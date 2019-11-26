from __future__ import unicode_literals

from builtins import object
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from system.models import Session, Page, Email, SMS
import json


@staff_member_required
def api_node(request, node_type=None, node_id=None):

    if node_type == 'page':
        node = get_object_or_404(Page, id=node_id)
        url = reverse('admin:system_page_change', args=[node.id])
    elif node_type == 'email':
        node = get_object_or_404(Email, id=node_id)
        url = reverse('admin:system_email_change', args=[node.id])
    elif node_type == 'sms':
        node = get_object_or_404(SMS, id=node_id)
        url = reverse('admin:system_sms_change', args=[node.id])
    elif node_type == 'session' or node_type == 'background_session':
        node = get_object_or_404(Session, id=node_id)
        url = reverse('admin:system_session_change', args=[node.id])
    else:
        class Dummy(object): pass
        node = Dummy()
        node.id = 0
        node.title = 'Start' if node_type == 'start' else ''
        url = ''

    response = {
        'id': node.id,
        'title': node.title,
        'url': url,
    }

    return HttpResponse(json.dumps(response), content_type='application/json')
