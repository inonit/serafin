from __future__ import unicode_literals
from __future__ import print_function

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import translation
from filer.models import File, Image
from system.models import Session, Page
from system.engine import Engine
import json


def main_page(request):

    session_id = request.user.data.get('session')

    if not session_id or not request.user.is_authenticated:
        return HttpResponseRedirect(settings.HOME_URL)

    session = get_object_or_404(Session, id=session_id)
    context = {
        'api': reverse('portal'),
        'program': session.program,
    }

    if session and session.program and session.program.is_rtl:
        translation.activate('he')

    return render(request, 'portal.html', context)


def modules_page(request):
    session_id = request.user.data.get('session')

    if not session_id or not request.user.is_authenticated:
        return HttpResponseRedirect(settings.HOME_URL)

    modules = request.user.get_modules()
    engine = Engine(user=request.user, context={}, is_interactive=True)
    page = engine.run()

    current_module_id = page.chapter.module.id if page.chapter and page.chapter.module else None
    context = {
        'modules': json.dumps(modules),
        'current_module_id': current_module_id if current_module_id else 0
    }

    return render(request, 'modules.html', context)


def module_redirect(request, module_id):
    if not request.is_ajax():
        return main_page(request)

    session_id = request.user.data.get('session')
    if not session_id or not request.user.is_authenticated:
        raise Http404

    chapter_id = request.user.get_chapter_by_module(module_id)
    if not chapter_id:
        raise Http404

    engine = Engine(user=request.user, context={}, is_interactive=True)
    page = engine.run(next=0, pop=0, chapter=chapter_id)

    if not page:
        raise Http404

    response = {
        'title': page.display_title,
        'data': page.data,
        'dead_end': page.dead_end,
        'stacked': page.stacked,
        'is_chapter': page.is_chapter,
        'chapters': page.chapters,
        'read_only': page.read_only,
        'is_back': page.is_back,
        'page_id': page.id
    }

    return JsonResponse(response)


def get_portal(request):
    if not request.is_ajax():
        return main_page(request)

    modules = request.user.get_modules()
    engine = Engine(user=request.user, context={}, is_interactive=True)
    page = engine.run()

    current_module_title = page.chapter.module.display_title if page.chapter and page.chapter.module else None
    current_module_id = page.chapter.module.id if page.chapter and page.chapter.module else None
    context = {
        'modules': modules,
        'modules_finished': len([m for m in modules if m['is_enabled'] == 1]) - (0 if current_module_id is None else 1),
        'current_page_title': page.display_title,
        'current_module_title': current_module_title,
        'current_module_id': current_module_id
    }

    return JsonResponse(context)


def home(request):
    return render(request, 'home.html', {})


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
        return HttpResponseRedirect(settings.HOME_URL)

    session = get_object_or_404(Session, id=session_id)

    context = {
        'program': session.program,
        'title': session.display_title,
        'api': reverse('content_api'),
        'module_id': 0 if not module_id else module_id
    }

    template = 'sessionnew.html'
    if request.GET.get("old") == '1':
        template = 'session.html'

    if session and session.program and session.program.is_rtl:
        translation.activate('he')

    return render(request, template, context)


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
        page.is_chapter = page.chapter is not None
        page.chapters = page.render_section(request.user)
        page.read_only = False
        page.is_back = False

    # engine selection
    else:
        next = request.GET.get('next')
        pop = request.GET.get('pop')
        chapter = request.GET.get('chapter')
        back = request.GET.get('back')
        engine = Engine(user=request.user, context=context, is_interactive=True)
        page = engine.run(next=next, pop=pop, chapter=chapter, back=back)

    if not page:
        raise Http404

    response = {
        'title': page.display_title,
        'data': page.data,
        'dead_end': page.dead_end,
        'stacked': page.stacked,
        'is_chapter': page.is_chapter,
        'chapters': page.chapters,
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

    context = {
        'session': session.id,
        'node': 0
    }

    engine = Engine(user=request.user, context=context, push=True, is_interactive=True)
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

    print(filer_file.icons)

    response = {
        'id': filer_file.id,
        'url': filer_file.url,
        'thumbnail': filer_file.icons['48'],
        'description': filer_file.original_filename,
    }

    return JsonResponse(response)
