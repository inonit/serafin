from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as login_view
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from system.engine import Engine
from system.models import Variable
from users.models import User
from tokens.tokens import token_generator
from events.signals import log_event
import json


def manual_login(request):
    '''Redirect to root if logged in or present login screen'''

    if request.user.is_authenticated():
        return redirect('/')
    return login_view(request, template_name='login.html', extra_context={'title': _('Log in')})


def manual_logout(request):
    '''Log user out if logged in and redirect to root'''

    if request.user.is_authenticated():
        logout(request)
    return redirect('/')


def login_via_email(request, user_id=None, token=None):
    '''Log in by token link or redirect to manual login if token is invalid'''

    user = authenticate(user_id=user_id, token=token)
    if user:
        login(request, user)
        return redirect('/')

    return redirect('login')


@csrf_exempt
def receive_sms(request):
    '''Receive sms from vault and let engine process it'''

    response = {'status': 'Fail.'}

    if request.method == 'POST':
        data = json.loads(request.body)

        user_id = data.get('user_id')
        token = data.get('token')
        message = data.get('message')

        if user_id and token:
            if token_generator.check_token(user_id, token):
                user = User.objects.get(id=user_id)

                reply_session = user.data.get('reply_session')
                reply_node = user.data.get('reply_node')
                reply_var = user.data.get('reply_variable')

                if reply_session and reply_node and reply_var:

                    del user.data['reply_session']
                    del user.data['reply_node']
                    del user.data['reply_variable']
                    user.save()

                    log_event.send(
                        engine.session,
                        domain='session',
                        actor=user,
                        variable=reply_var,
                        pre_value=user.data.get(reply_var),
                        post_value=message
                    )

                    context = {
                        'session': reply_session,
                        'node': reply_node,
                        reply_var: message,
                    }
                    engine = Engine(user_id=user_id, context=context)
                    engine.transition(reply_node)

                    response = {'status': 'OK'}

    return JsonResponse(response)


@login_required
def profile(request):
    '''Show the user profile or save user editable data'''

    user_editable_vars = {
        var.name: {
            'label': var.display_name,
            'value': request.user.data.get(var.name) or var.value
        } for var in Variable.objects.filter(user_editable=True)
    }

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key in user_editable_vars.keys():
                request.user.data[key] = value

        request.user.save()
        return redirect('profile')

    now = timezone.localtime(timezone.now())
    progress_set = {}
    for useraccess in request.user.programuseraccess_set.all():

        sessions_done = 0
        sessions_remaining = 0
        days_since_start = 0

        start_times = [
            s.get_start_time(
                useraccess.start_time,
                useraccess.time_factor
            ) for s in useraccess.program.session_set.all()
        ]

        for start_time in start_times:

            if start_time <= now:
                sessions_done += 1

            if start_time > now:
                sessions_remaining += 1

        days_since_start = (now - min(start_times)).days

        progress_set[useraccess.program] = {
            'sessions_done': sessions_done,
            'sessions_remaining': sessions_remaining,
            'days_since_start': days_since_start
        }

    context = {
        'user_editable_vars': user_editable_vars,
        'progress_set': progress_set
    }

    return render(request, 'profile.html', context)
