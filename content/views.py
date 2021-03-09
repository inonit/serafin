from __future__ import unicode_literals
from __future__ import print_function

from datetime import timedelta
from django.db.models import Q, Max, Sum, CharField, FloatField, Value as V, DateField
from django.db.models.functions import Substr, StrIndex, Cast
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import translation, timezone
from filer.models import File, Image
from itertools import chain
from ratelimit import UNSAFE
from ratelimit.decorators import ratelimit
from system.models import Session, Page, ProgramUserAccess,  Variable
from events.models import Event
from events.signals import log_event
from users.models import User
from system.engine import Engine
from serafin.settings import TIME_ZONE
import json


def set_language_by_program(program):
    if program and program.is_rtl:
        translation.activate('he')


def main_page(request):
    session_id = request.user.data.get('session')

    if not session_id or not request.user.is_authenticated:
        if request.user.is_authenticated and request.user.is_therapist:
            return HttpResponseRedirect(reverse('therapist_zone'))
        return HttpResponseRedirect(settings.HOME_URL)

    session = get_object_or_404(Session, id=session_id)
    context = {
        'api': reverse('portal'),
        'program': session.program,
        'page': 'home'
    }

    return render(request, 'portal.html', context)

@login_required
def tools_page(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(settings.HOME_URL)

    tools = request.user.get_tools()

    context = {
        'tools': tools,
        'captions': {'file': any(x['type'] == "file" for x in tools),
                     'audio': any(x['type'] == "audio" for x in tools),
                     'video': any(x['type'] == "video" for x in tools)},
        'page': 'tools'
    }

    return render(request, 'tools.html', context)


def get_portal(request):
    if not request.is_ajax():
        return main_page(request)

    modules = request.user.get_modules()
    engine = Engine(user=request.user, context={}, is_interactive=True)
    page = engine.run()

    current_module_title = page.chapter.module.display_title if page and page.chapter and page.chapter.module else None
    current_module_id = page.chapter.module.id if page and page.chapter and page.chapter.module else None
    program = page.program if page else None
    if not program:
        session_id = request.user.data.get("session")
        session = get_object_or_404(Session, id=session_id)
        program = session.program
    has_unread_messages = False
    if request.user.therapist is not None:
        has_unread_messages = ChatMessage.objects.filter(Q(sender=request.user.therapist) & Q(receiver=request.user)
                                                         & Q(is_read=False)).count() > 0
    context = {
        'modules': modules,
        'modules_finished': len([m for m in modules if m['is_enabled'] == 1]) - (0 if current_module_id is None else 1),
        'current_page_title': current_module_title if current_module_title else page.display_title if page else None,
        'current_module_title': current_module_title,
        'current_module_id': current_module_id,
        'has_messages': has_unread_messages,
        'program_name': program.display_title,
        'program_about': program.about,
        'cover_image': program.cover_image.url if program.cover_image is not None else None
    }

    return JsonResponse(context)


def home(request):
    return render(request, 'home.html2', {})


@login_required
def get_session(request, module_id=None):
    if request.is_ajax():
        return get_page(request)

    # admin session preview support
    session_id = request.GET.get('session_id', None)
    if request.user.is_staff and session_id:
        request.user.data['session'] = session_id
        request.user.data['node'] = 0
        request.user.data['stack'] = []
        request.user.save()

    session_id = request.user.data.get('session')

    if not session_id or not request.user.is_authenticated:
        page_id = request.GET.get('page_id', None)
        if request.user.is_staff and page_id:
            context = {
                'program': 'None',
                'title': 'None',
                'api': reverse('content_api'),
                'module_id': 0
            }
            return render(request, 'sessionnew.html', context)

        return HttpResponseRedirect(settings.HOME_URL)

    session = get_object_or_404(Session, id=session_id)

    context = {
        'program': session.program,
        'title': session.display_title,
        'api': reverse('content_api'),
        'module_id': 0 if not module_id else module_id
    }

    return render(request, 'sessionnew.html', context)


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
        page.read_only = False
        page.is_back = False

    # engine selection
    else:
        next = request.GET.get('next')
        pop = request.GET.get('pop')
        engine = Engine(user=request.user, context=context,
                        is_interactive=True)
        page = engine.run(next=next, pop=pop, chapter=chapter, back=back)

    if not page:
        raise Http404

    response = {
        'title': page.display_title,
        'data': page.data,
        'dead_end': page.dead_end,
        'stacked': page.stacked,
        'read_only': page.read_only,
        'is_back': page.is_back,
        'page_id': page.id
    }

    return JsonResponse(response)


def content_route(request, route_slug=None):

    if request.is_ajax():
        return get_page(request)

    session = get_object_or_404(Session, route_slug=route_slug)

    if (not session.is_open and
            session.program and
            session.program.programuseraccess_set.filter(user=request.user.id).exists()):
        return HttpResponseRedirect(settings.HOME_URL)

    if session and session.program and session.program.is_rtl:
        translation.activate('he')

    context = {
        'session': session.id,
        'node': 0
    }

    engine = Engine(user=request.user, context=context,
                    push=True, is_interactive=True)
    engine.run()

    context = {
        'program': session.program,
        'title': session.display_title,
        'api': reverse('content_api'),
        'module_id': 0
    }

    return render(request, 'sessionnew.html', context)


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

    return JsonResponse(response)
