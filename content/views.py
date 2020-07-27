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
from system.models import Session, Page, ProgramUserAccess, ProgramGoldVariable, Variable, TherapistNotification, \
    ChatMessage, Note
from events.models import Event
from events.signals import log_event
from users.models import User
from system.engine import Engine
from serafin.settings import TIME_ZONE
import json


def set_language_by_session(session):
    if session and session.program and session.program.is_rtl:
        translation.activate('he')


def set_language_by_program(program):
    if program and program.is_rtl:
        translation.activate('he')


def main_page(request):
    session_id = request.user.data.get('session')

    if not session_id or not request.user.is_authenticated:
        return HttpResponseRedirect(settings.HOME_URL)

    session = get_object_or_404(Session, id=session_id)
    has_therapist = request.user.therapist is not None
    context = {
        'api': reverse('portal'),
        'program': session.program,
        'has_therapist': has_therapist,
        'page': 'home'
    }

    set_language_by_session(session)

    return render(request, 'portal.html', context)


def therapist_zone(request):
    if not request.user.is_authenticated or not request.user.is_therapist:
        return main_page(request)

    if request.user.patients.first() is not None and \
            request.user.patients.first().programuseraccess_set.first() is not None:
        set_language_by_program(request.user.patients.first().programuseraccess_set.first().program)

    context = {
        'api': reverse('users_stats'),
        'chat_api': reverse('chat')
    }
    return render(request, 'therapist.html', context)


def users_stats(request):
    if not request.user.is_authenticated or not request.user.is_therapist:
        return main_page(request)

    if not request.is_ajax():
        return therapist_zone(request)

    user_id = request.GET.get('user_id')
    if user_id is not None:
        return user_state(request, user_id)

    users = User.objects.filter(therapist=request.user)

    users_table = []
    all_users_events = Event.objects.filter(actor__in=users)
    current_tz = timezone.get_current_timezone()
    for user in users:
        # we assume the user has only one program
        current_user_events = all_users_events.filter(actor=user)
        program_user_access = user.get_first_program_user_access()
        program_title = None
        start_time = None
        if program_user_access is not None:
            program_title = program_user_access.program.display_title
            start_time = program_user_access.start_time.astimezone(current_tz).strftime('%d-%b-%Y (%H:%M)')

        total_ms = current_user_events.filter(variable='timer') \
            .annotate(ms_part_noise=Substr('post_value', StrIndex('post_value', V(',')) + 2, 1000,
                                           output_field=CharField(max_length=100))) \
            .annotate(ms_part=Cast(Substr('ms_part_noise', 1, StrIndex('ms_part_noise', V(' ')) - 1,
                                          output_field=CharField(max_length=10)), FloatField())) \
            .aggregate(total_ms=Sum('ms_part'))

        total_time = 0
        if total_ms.get('total_ms') is not None:
            total_time = str(timedelta(seconds=int(timedelta(milliseconds=total_ms.get('total_ms')).total_seconds())))

        last_transition_page = None
        last_transition_row = current_user_events.filter(variable='transition').order_by('-time').first()
        if last_transition_row is not None:
            last_transition_page = last_transition_row.post_value

        last_login = None
        if user.last_login is not None:
            last_login = user.last_login.astimezone(current_tz).strftime('%d-%b-%Y (%H:%M)')

        login_count = current_user_events.filter(variable='login').count()
        distinct_days = current_user_events.filter(variable='login').annotate(day=Cast('time', DateField())) \
            .values('day').distinct('day').count()

        has_notification = user.patient_notifications.filter(Q(therapist=request.user) & Q(is_read=False)).count() > 0
        has_unread_messages = ChatMessage.objects.filter(Q(sender=user) & Q(receiver=request.user) & Q(is_read=False)) \
            .count() > 0

        user_row = {'id': user.id, 'email': user.email, 'phone': user.phone, 'last_login': last_login,
                    'program_phase': user.data.get('Program_Phase'), 'start_time': start_time,
                    'program': program_title, 'total_time': total_time, 'distinct_days': distinct_days,
                    'login_count': login_count, 'current_page': last_transition_page,
                    'has_notification': has_notification, 'has_messages': has_unread_messages}

        users_table.append(user_row)

    objects = {
        'users': users_table
    }
    return JsonResponse(objects)


def user_state(request, user_id):
    if not request.user.is_authenticated or not request.user.is_therapist:
        return main_page(request)

    if not request.is_ajax():
        return therapist_zone(request)

    # verify the therapist is the owner of this user
    user = User.objects.get(id=user_id)
    if user.therapist != request.user:
        return JsonResponse({'error': 'access denied'}, status=403)

    # extract gold variables
    program = user.get_first_program()
    gold_variables_dataset = program.programgoldvariable_set.all()

    if request.method == 'POST':
        notification_read_id = request.POST.get("notification_id", None)
        note_msg = request.POST.get("note_msg", None)
        if notification_read_id:
            notification = TherapistNotification.objects.get(id=notification_read_id)
            # verify this notification belongs to the user and this therapist
            if notification.therapist == request.user and notification.patient == user:
                notification.is_read = True
                notification.save()
        elif note_msg:
            Note.objects.create(
                message=note_msg,
                therapist=request.user,
                user=user
            )
        else:
            for key, value in list(request.POST.items()):
                gold_variable = gold_variables_dataset.filter(variable__name=key).first()
                if gold_variable is not None and gold_variable.therapist_can_edit:
                    # todo: support array variable / refactor get/set user variable to user
                    pre_value = user.get_pre_variable_value_for_log(key)
                    log_event.send(
                        request.user,
                        domain='therapist',
                        actor=user,
                        variable=key,
                        pre_value=str(pre_value),
                        post_value=str(value)
                    )
                    user.data[key] = value
            user.save()

    current_tz = timezone.get_current_timezone()
    user_events = Event.objects.filter(Q(actor=user) & ((Q(domain='session') & Q(variable='transition')) |
                                                        (Q(domain='userdata') & ~Q(variable='timer')))) \
        .order_by('-time')

    user_expressions_events = Event.objects.filter(Q(actor=user) & (Q(domain='expression') | Q(domain='therapist'))) \
        .order_by('-time')

    pages = []
    variables = []
    current_page = None
    page_time = None
    for event in user_events:
        if event.domain == 'session' and event.variable == 'transition':
            if variables:
                page = next((item for item in pages if item['name'] == current_page), None)
                if page is None:
                    page = {'name': current_page, 'variables': []}
                    pages.append(page)
                page['variables'].append({'time': page_time.astimezone(current_tz).strftime('%d-%m-%Y %H:%M'),
                                          'vars': variables})
            current_page = event.pre_value
            page_time = event.time
            variables = []
        elif event.domain == 'userdata' and current_page is not None:
            # find label by post_value
            variable_display_value = event.post_value
            if event.post_value.isnumeric():
                try:
                    page = Page.objects.get(title=current_page)
                    variable_display_value = page.extract_label(event.variable, event.post_value)
                except Page.DoesNotExist:
                    pass

            variables.append({'name': Variable.display_name_by_name(event.variable), 'value': variable_display_value})
        else:
            pass

    gold_variables = []
    for gold_variable in gold_variables_dataset:
        variable_value = user.data.get(gold_variable.variable.name)
        if Variable.is_array_variable(gold_variable.variable.name) and isinstance(variable_value, list):
            variable_value = variable_value[-1]

        variable_display_name = gold_variable.variable.display_name
        if not variable_display_name:
            variable_display_name = gold_variable.variable.name

        variable_optional_values = []
        if gold_variable.variable.optional_values:
            variable_optional_values = [x.strip() for x in gold_variable.variable.optional_values.split(',')]

        gold_variable_element = {'name': gold_variable.variable.name,
                                 'display_name': variable_display_name,
                                 'value': variable_value,
                                 'editable': gold_variable.therapist_can_edit,
                                 'is_primary': gold_variable.golden_type == 'primary',
                                 'options': variable_optional_values}

        variable_values_by_date = []
        userdata_variable_events = user_events.filter(Q(domain='userdata') & Q(variable=gold_variable.variable.name))
        expressions_variable_event = user_expressions_events.filter(variable=gold_variable.variable.name)
        for e in list(chain(userdata_variable_events, expressions_variable_event)):
            variable_values_by_date.append({'time': e.time, 'value': e.post_value})
        variable_values_by_date.sort(key=lambda x: x['time'], reverse=True)
        variable_values_by_date = list(
            map(lambda x: {'value': x['value'], 'time': x['time'].astimezone(current_tz).strftime('%d-%m-%Y %H:%M')},
                variable_values_by_date))
        gold_variable_element['values'] = variable_values_by_date

        gold_variables.append(gold_variable_element)

    notifications_objects = TherapistNotification.objects.filter(Q(therapist=user.therapist) & Q(patient=user)) \
        .order_by('-timestamp')
    notifications = [{'id': obj.id, 'message': obj.message, 'timestamp': obj.timestamp, 'is_read': obj.is_read}
                     for obj in notifications_objects]

    has_messages = ChatMessage.objects.filter(
        Q(receiver=user.therapist) & Q(sender=user) & Q(is_read=False)).count() > 0

    notes_objects = request.user.written_notes.filter(Q(therapist=request.user) & Q(user=user))

    notes = [{'id': obj.id, 'message': obj.message, 'time': obj.timestamp} for obj in notes_objects]

    context = {
        'pages': pages,
        'variables': gold_variables,
        'notifications': notifications,
        'notes': notes,
        'has_messages': has_messages,
        'email': user.email,
        'phone': user.phone,
        'id': user.id,
    }
    return JsonResponse(context)


def modules_page(request):
    session_id = request.user.data.get('session')

    if not session_id or not request.user.is_authenticated:
        return HttpResponseRedirect(settings.HOME_URL)

    modules = request.user.get_modules()
    engine = Engine(user=request.user, context={}, is_interactive=True)
    page = engine.run()

    current_module_id = page.chapter.module.id if page.chapter and page.chapter.module else None
    has_therapist = request.user.therapist is not None
    has_unread_messages = False
    if has_therapist:
        has_unread_messages = ChatMessage.objects.filter(Q(sender=request.user.therapist) & Q(receiver=request.user)
                                                         & Q(is_read=False)).count() > 0

    context = {
        'modules': modules,
        'current_module_id': current_module_id if current_module_id else 0,
        'has_therapist': has_therapist,
        'has_messages': has_unread_messages,
        'page': 'modules'
    }

    return render(request, 'modules.html', context)


@login_required
def tools_page(request):
    session_id = request.user.data.get('session')

    if not request.user.is_authenticated:
        return HttpResponseRedirect(settings.HOME_URL)

    session = get_object_or_404(Session, id=session_id)
    set_language_by_session(session)

    tools = request.user.get_tools()
    has_therapist = request.user.therapist is not None
    has_unread_messages = False
    if has_therapist:
        has_unread_messages = ChatMessage.objects.filter(Q(sender=request.user.therapist) & Q(receiver=request.user)
                                                         & Q(is_read=False)).count() > 0

    context = {
        'tools': tools,
        'captions': {'file': any(x['type'] == "file" for x in tools),
                      'audio': any(x['type'] == "audio" for x in tools),
                      'video': any(x['type'] == "video" for x in tools)},
        'has_therapist': has_therapist,
        'has_messages': has_unread_messages,
        'page': 'tools'
    }

    return render(request, 'tools.html', context)


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
    program = page.program
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
        'current_page_title': page.display_title,
        'current_module_title': current_module_title,
        'current_module_id': current_module_id,
        'has_messages': has_unread_messages,
        'program_name': program.display_title
    }

    return JsonResponse(context)


def home(request):
    return render(request, 'home.html2', {})


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

    set_language_by_session(session)

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


@login_required
def send_message(request):
    if request.method != 'POST':
        raise ValueError('bad method')

    message = request.POST.get("msg", None)
    file = request.FILES.get("file", None)
    audio = request.FILES.get("audio_file", None)
    if (message is None or message.strip() == '') and file is None and audio is None:
        raise ValueError('message is empty')

    obj = None
    other_user = None
    user_id = request.POST.get("user_id", None)
    chat_message = ChatMessage(message=message, sender=request.user)
    if user_id is not None and request.user.is_therapist:
        patient = User.objects.get(id=user_id)
        other_user = patient
        chat_message.receiver = patient
    elif user_id is None:
        therapist = request.user.therapist
        if therapist is None:
            raise ValueError('no therapist')
        other_user = therapist
        chat_message.receiver = therapist
    else:
        raise ValueError('bad request')

    if file is not None:
        if file.content_type not in ['application/msword', 'text/plain', 'application/pdf']:
            raise ValueError('bad file')
        if file.size > 4194304:
            raise ValueError('big file')
        chat_message.file_type = file.content_type
        chat_message.file_name = file.name
        chat_message.file_data = file.read()
    elif audio is not None and audio.content_type == "audio/wav":
        chat_message.file_type = audio.content_type
        chat_message.file_name = "audio"
        chat_message.file_data = audio.read()

    chat_message.save()

    if not other_user.is_therapist:
        # the other user is patient
        other_user.send_new_message_notification()

    return receive_messages_internal(prev=None, next=chat_message.id - 1, current_user=request.user,
                                     other_user=other_user)


@login_required
def receive_messages(request):
    prev = request.GET.get("prev", None)
    next = request.GET.get("next", None)
    user_id = request.GET.get("user", None)
    current_user = request.user

    if user_id is None:
        if request.user.therapist is None:
            raise PermissionError("no therapist")
        user_id = request.user.therapist.id
    elif not request.user.is_therapist:
        raise PermissionError("bad request")
    other_user = User.objects.get(id=user_id)

    return receive_messages_internal(prev, next, current_user, other_user)


@login_required
def get_attachment(request, msg_id):
    message = ChatMessage.objects.get(id=msg_id)
    if (request.user == message.sender or request.user == message.receiver) and message.file_data is not None:
        return HttpResponse(content=bytes(message.file_data), content_type=message.file_type)
    raise FileNotFoundError("attachment not found")


def receive_messages_internal(prev, next, current_user, other_user):
    max_messages = 5
    messages = None
    if next is None and prev is None:
        messages = ChatMessage.objects.filter((Q(sender=current_user) & Q(receiver=other_user)) |
                                              (Q(sender=other_user) & Q(receiver=current_user))) \
                       .order_by('timestamp').reverse()[:max_messages]
        old_count = len(messages)
        new_count = 0
        while old_count != new_count and not messages[0].is_read and messages[0].receiver == current_user:
            old_count = len(messages)
            max_messages = max_messages * 2
            messages = ChatMessage.objects.filter((Q(sender=current_user) & Q(receiver=other_user)) |
                                                  (Q(sender=other_user) & Q(receiver=current_user))) \
                           .order_by('timestamp').reverse()[:max_messages]
            new_count = len(messages)

    elif prev is not None:
        messages = ChatMessage.objects.filter(Q(id__lt=prev) & ((Q(sender=current_user) & Q(receiver=other_user)) |
                                                                (Q(sender=other_user) & Q(receiver=current_user)))) \
                       .order_by('timestamp').reverse()[:max_messages]
    else:
        messages = ChatMessage.objects.filter(Q(id__gt=next) & ((Q(sender=current_user) & Q(receiver=other_user)) |
                                                                (Q(sender=other_user) & Q(receiver=current_user)))) \
                       .order_by('timestamp').reverse()[:]

    objects = {
        'messages': [{'id': m.id, 'msg': m.message, 'time': m.timestamp,
                      's': m.sender.id == current_user.id, 'r': m.receiver.id == current_user.id,
                      'read': m.is_read, 'file_name': m.file_name, 'is_audio': m.file_type == 'audio/wav'}
                     for m in messages]
    }

    for m in messages:
        if not m.is_read and current_user == m.receiver:
            m.is_read = True
            m.save()

    return JsonResponse(objects)


def chat(request):
    send_message_val = request.GET.get('send_message', None)
    if send_message_val is not None:
        return send_message(request)

    receive_message_val = request.GET.get('receive_message', None)
    if receive_message_val is not None:
        return receive_messages(request)

    attachment_id = request.GET.get('attachment_id', None)
    if attachment_id:
        return get_attachment(request, attachment_id)


def my_therapist(request):
    session_id = request.user.data.get('session')

    if not request.user.is_authenticated:
        return HttpResponseRedirect(settings.HOME_URL)

    session = get_object_or_404(Session, id=session_id)
    set_language_by_session(session)

    context = {
        'chat_api': reverse('chat')
    }

    return render(request, 'mytherapist.html', context)
