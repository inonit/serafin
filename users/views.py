from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as login_view
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from serafin.utils import JSONResponse
from system.engine import Engine
from system.models import Variable
from users.models import User
from tokens.tokens import token_generator
import json


def manual_login(request):
    if request.user.is_authenticated():
        return redirect('/')
    return login_view(request, template_name='login.html', extra_context={'title': _('Log in')})


def manual_logout(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('/')


def login_via_email(request, user_id=None, token=None):

    user = authenticate(user_id=user_id, token=token)
    if user:
        login(request, user)
        return redirect('/')

    return redirect('login')


@csrf_exempt
def receive_sms(request):

    response = {'status': 'Fail.'}

    if request.method == 'POST':
        data = json.loads(request.body)

        user_id = data.get('user_id')
        token = data.get('token')
        message = data.get('message')

        if user_id and token:
            if token_generator.check_token(user_id, token):
                user = User.objects.get(id=user_id)

                node_id = user.data.get('current_background', 0)
                reply_var = user.data.get('reply_variable')

                context = {}
                if reply_var:
                    context[reply_var] = message

                engine = Engine(user_id, context)
                engine.transition(node_id)

                response = {'status': 'OK'}

    return JSONResponse(response)


@login_required
def profile(request):

    user_editable_vars = []
    for var in Variable.objects.all():
        if var.user_editable:
            user_editable_vars.append({
                'name': var.name,
                'value': request.user.data[var.name] or var.value
            })

    if request.method == 'POST':
        for key, value in request.POST.items():
            for var in user_editable_vars:
                if key == var['name']:
                    request.user.data[key] = value

        request.user.save()
        return redirect('profile')

    progress_set = {}
    now = timezone.localtime(timezone.now())
    for ua in request.user.programuseraccess_set.all():

        sessions_done = 0
        sessions_remaining = 0
        days_since_start = 0

        start_times = [
            s.get_start_time(
                ua.start_time,
                ua.time_factor
            ) for s in ua.program.session_set.all()
        ]

        for start_time in start_times:

            if start_time <= now:
                sessions_done += 1

            if start_time > now:
                sessions_remaining += 1

        days_since_start = (now - min(start_times)).days

        progress_set[ua.program] = {
            'sessions_done': sessions_done,
            'sessions_remaining': sessions_remaining,
            'days_since_start': days_since_start
        }

    context = {
        'title': _('User profile'),
        'user_editable_vars': user_editable_vars,
        'progress_set': progress_set
    }

    return render(request, 'profile.html', context)
