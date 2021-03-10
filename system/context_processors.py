from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings


def site(request):
    return {
        'site': get_current_site(request),
    }


def stylesheet(request):
    if '_stylesheet' in request.session:
        for stylesheet in getattr(settings, 'STYLESHEETS', []):
            if stylesheet['name'] == request.session["_stylesheet"]:
                return {'stylesheet': stylesheet['path']}
    return {'stylesheet': None}
