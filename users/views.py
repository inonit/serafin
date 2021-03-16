from __future__ import unicode_literals

from django.contrib.auth.views import redirect_to_login, update_session_auth_hash, PasswordChangeView
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from events.signals import log_event
from system.engine import Engine
from system.models import Variable
from tokens.tokens import token_generator
from users.models import User

from twilio import twiml
from plivo import plivoxml

import json
import logging


def manual_login(request):
    '''Redirect to root if logged in or present login screen'''

    if request.user.is_authenticated:
        return redirect('/')
    return auth_views.LoginView.as_view(template_name='login.html', extra_context={'title': _('Log in')})(request)


def manual_logout(request):
    '''Log user out if logged in and redirect to root'''

    if request.user.is_authenticated:
        logout(request)
    return redirect('/')


def login_via_email(request, user_id=None, token=None):
    '''Log in by token link or redirect to manual login if token is invalid'''

    if request.user.is_authenticated:
        return redirect(reverse('content'))

    user = authenticate(user_id=user_id, token=token)
    if user:
        login(request, user)
        return redirect('/')

    return redirect_to_login(reverse('content'))


@csrf_exempt
def receive_sms(request):
    '''Receive sms message from user, process through Engine and respond'''

    reply = ''
    response = ''
    sender = ''
    body = ''
    dst = ''
    src = ''

    debug_logger = logging.getLogger('debug')
    now = timezone.now()

    if request.method == 'POST':

        debug_logger.debug('received post %s', request.POST)

        if settings.SMS_SERVICE == 'Twilio' or settings.SMS_SERVICE == 'Console':
            sender = request.POST.get('From')
            body = request.POST.get('Body')

        if settings.SMS_SERVICE == 'Plivo':
            sender = '+' + request.POST.get('From')
            dst = request.POST.get('From')
            src = request.POST.get('To')
            body = request.POST.get('Text')

        if settings.SMS_SERVICE == 'Primafon':
            data = json.loads(request.body)
            sender = '+' + data['from']
            dst = data['from']
            src = '12345678'
            body = data['body']

        try:
            user = User.objects.get(phone=sender)
            debug_logger.debug('got user %r', user)
        except:
            user = None
            reply = _('Sorry, I\'m not sure who this is.')

        if user:
            reply_session = user.data.get('reply_session')
            reply_node = user.data.get('reply_node')
            reply_var = user.data.get('reply_variable')

            if reply_session and reply_node and reply_var:

                log_event.send(
                    user,
                    domain='user',
                    actor=user,
                    variable=reply_var,
                    pre_value=user.data.get(reply_var, ''),
                    post_value=body
                )

                try:
                    context = {
                        'session': reply_session,
                        'node': reply_node,
                        reply_var: body,
                    }
                    engine = Engine(user=user, context=context)
                    debug_logger.debug('prepared engine')

                    del engine.user.data['reply_session']
                    del engine.user.data['reply_node']
                    del engine.user.data['reply_variable']
                    debug_logger.debug('deleted reply vars')

                    engine.transition(reply_node)
                    debug_logger.debug('finished engine transitions')

                    engine.user.save()
                    debug_logger.debug('saved user %s', engine.user)

                except Exception as e:
                    reply = _('Sorry, there was an error processing your SMS. '
                              'Our technicians have been notified and will try to fix it.')
    else:
        debug_logger.debug('no data received')
        reply = _('No data received.')

    if settings.SMS_SERVICE == 'Twilio':
        response = twiml.Response()
        if reply:
            response.message(reply)

    if settings.SMS_SERVICE == 'Plivo':
        response = plivoxml.Response()
        if reply and src and dst:
            response.addMessage(reply, src=src, dst=dst)

    debug_logger.debug('finished request')
    return HttpResponse(response, content_type='text/xml')


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
        for key, value in list(request.POST.items()):
            if key in list(user_editable_vars.keys()):
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
        try:
            days_since_start = (now - min(start_times)).days
        except:
            pass

        progress_set[useraccess.program.display_title] = {
            'sessions_done': sessions_done,
            'sessions_remaining': sessions_remaining,
            'days_since_start': days_since_start
        }

    context = {
        'user_editable_vars': user_editable_vars,
        'progress_set': progress_set
    }

    return render(request, 'profile.html', context)


class CustomPasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        self.request.user.password_changed()
        if 'pwd_req' in self.request.session:
            del self.request.session['pwd_req']
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        if self.request.user and self.request.user.password_change_required:
            self.request.session['pwd_req'] = True
        return kwargs
