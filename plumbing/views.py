from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse
from django.http import HttpResponse
import json


def plumbing_get(request):
    plumbing_init = {
        'nodes': [
            {
                'id': 1,
                'title': 'Start',
                'url': reverse('admin:system_page_add'),
                'metrics': {
                    'left': '50px',
                    'top': '150px'
                }
            },
            {
                'id': 2,
                'title': 'Page 1',
                'url': reverse('admin:system_page_add'),
                'metrics': {
                    'left': '250px',
                    'top': '150px'
                }
            },
            {
                'id': 3,
                'title': 'Page 2',
                'url': reverse('admin:system_page_add'),
                'metrics': {
                    'left': '450px',
                    'top': '150px'
                }
            },
            {
                'id': 4,
                'title': 'Choice',
                'url': reverse('admin:system_page_add'),
                'metrics': {
                    'left': '650px',
                    'top': '150px'
                }
            },
            {
                'id': 5,
                'title': 'SMS',
                'url': reverse('admin:system_page_add'),
                'metrics': {
                    'left': '850px',
                    'top': '250px'
                }
            },
            {
                'id': 6,
                'title': 'Page 3',
                'url': reverse('admin:system_page_add'),
                'metrics': {
                    'left': '1050px',
                    'top': '150px'
                }
            },
        ],
        'edges': [
            {
                'label': 'next',
                'source': 1,
                'target': 2,
            },
            {
                'label': 'next',
                'source': 2,
                'target': 3,
            },
            {
                'label': 'next',
                'source': 3,
                'target': 4,
            },
            {
                'label': 'choose again',
                'source': 4,
                'target': 4,
            },
            {
                'label': 'next',
                'source': 4,
                'target': 5,
            },
            {
                'label': 'next',
                'source': 4,
                'target': 6,
            },
            {
                'label': 'next',
                'source': 5,
                'target': 6,
            },
        ]
    }
    return HttpResponse(json.dumps(plumbing_init), content_type='application/json')


def plumbing_post(request):
    response = {
        'status': 'ok',
    }
    return HttpResponse(json.dumps(response), content_type='application/json')
