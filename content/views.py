from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from filer.models import File, Image
from serafin.utils import JSONResponse
from system.models import Session, Page
from system.engine import Engine
import json


@login_required
def get_session(request):

    if request.is_ajax():
        return get_page(request)

    # admin session preview support
    session_id = request.GET.get('session_id', None)
    if request.user.is_staff and session_id:
        request.user.data['current_session'] = session_id
        request.user.data['current_node'] = 0
        request.user.save()

    try:
        session_id = request.user.data['current_session']
        session = Session.objects.get(id=session_id)
        program = session.program
    except:
        program = ''

    context = {
        'program': program,
        'title': session.display_title,
        'api': reverse('content_api'),
    }

    return render(request, 'session.html', context)


@login_required
def get_page(request):

    context = {}

    if request.method == 'POST':
        post_data = json.loads(request.body)
        post_data = {item.get('key'): item.get('value') for item in post_data}
        context.update(post_data)

    # admin page preview support
    page_id = request.GET.get('page_id', None)
    if request.user.is_staff and page_id:
        page = Page.objects.get(id=page_id)
        page.update_html(request.user)
        page.dead_end = True

    # engine selection
    else:
        next = request.GET.get('next', None)
        engine = Engine(request.user, context)
        page = engine.run(next)

    response = {
        'title': page.display_title,
        'data': page.data,
        'dead_end': page.dead_end,
    }

    return JSONResponse(response)


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
