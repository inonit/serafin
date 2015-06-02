from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from filer.models import File, Image
from serafin.utils import JSONResponse
from system.models import Session, Page
from system.engine import Engine, EngineException
import json


def home(request):
    return render(request, 'home.html', {})


def get_session(request):

    if request.is_ajax():
        return get_page(request)

    # admin session preview support
    session_id = request.GET.get('session_id', None)
    if request.user.is_staff and session_id:
        request.user.data['session'] = session_id
        request.user.data['node'] = 0
        request.user.save()

    session_id = request.user.data.get('session')

    if not session_id or not request.user.is_authenticated():
        return HttpResponseRedirect(settings.HOME_URL)

    session = get_object_or_404(Session, id=session_id)

    context = {
        'program': session.program,
        'title': session.display_title,
        'api': reverse('content_api'),
    }

    return render(request, 'session.html', context)


def get_page(request):

    context = {}

    if request.method == 'POST':
        post_data = json.loads(request.body) if request.body else {}
        context.update(post_data)

    # admin page preview support
    page_id = request.GET.get('page_id')
    if request.user.is_staff and page_id:
        page = get_object_or_404(Page, id=page_id)
        page.update_html(request.user)
        page.dead_end = True
        page.stacked = False

    # engine selection
    else:
        next = request.GET.get('next')
        pop = request.GET.get('pop')
        engine = Engine(None, context, user=request.user)
        page = engine.run(next=next, pop=pop)

    if not page:
        raise EngineException('No page returned!')

    response = {
        'title': page.display_title,
        'data': page.data,
        'dead_end': page.dead_end,
        'stacked': page.stacked
    }

    return JSONResponse(response)


def content_route(request, route_slug=None):

    if request.is_ajax():
        return get_page(request)

    session = get_object_or_404(Session, route_slug=route_slug)

    if (not session.is_open and
        session.program and
        session.program.programuseraccess_set.filter(user=request.user).exists()):
        return HttpResponseRedirect(settings.HOME_URL)

    context = {
        'session': session.id,
        'node': 0
    }

    engine = Engine(None, context, push=True, user=request.user)
    engine.run()

    context = {
        'program': session.program,
        'title': session.display_title,
        'api': reverse('content_api'),
    }

    return render(request, 'session.html', context)


@staff_member_required
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

    return JSONResponse(response)
