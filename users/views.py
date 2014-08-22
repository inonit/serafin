from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import login as login_view
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from serafin.utils import JSONResponse
from system.engine import Engine
from users.models import User
from tokens.tokens import token_generator
import json


def manual_login(request):
    if request.user.is_authenticated():
        return redirect('/')
    return login_view(request, template_name='login.html')


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

    response = {'message': 'Go away.'}

    if request.method == 'POST':
        data = json.loads(request.body)

        user_id = data.get('user_id')
        token = data.get('token')
        message = data.get('message')

        if user_id and token:
            if token_generator.check_token(user_id, token):
                user = User.objects.get(id=user_id)

                node_id = user.data.get('current_background', 0)

                engine = Engine(user_id, {'sms_response': message})
                engine.transition(node_id)

                response = {'message': 'OK'}

    return JSONResponse(response)
