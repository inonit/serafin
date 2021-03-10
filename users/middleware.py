from django.contrib import auth
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import translation
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import AuthenticationMiddleware
from ratelimit import ALL, UNSAFE
from ratelimit.core import is_ratelimited

from system.models import Session


def get_user(request):
    """
    Returns the user model instance associated with the given request session.
    If no user is retrieved an instance of `StatefulAnonymousUser` is returned.
    """
    if hasattr(request, '_cached_user'):
        return request._cached_user

    user = auth.get_user(request)

    from django.contrib.auth.models import AnonymousUser
    from users.models import StatefulAnonymousUser

    if isinstance(user, AnonymousUser):
        user = StatefulAnonymousUser(request.session)

    request._cached_user = user

    return request._cached_user


class AuthenticationMiddleware(AuthenticationMiddleware):

    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))
        if request.user.is_authenticated and not request.path.startswith('/admin'):
            session_id = request.user.data.get('session')
            try:
                session = get_object_or_404(Session, id=session_id)
                if session and session.program and session.program.is_rtl:
                    translation.activate('he')
            except Http404 as ex:
                pass


class ForceChangePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if 'password_change' not in request.path and request.user.password_change_required:
                return redirect(reverse('password_change'))

        return self.get_response(request)


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if is_ratelimited(request, group='post_by_user', key='user_or_ip', method=UNSAFE, rate='10/m', increment=False):
            raise Http404
        elif is_ratelimited(request, group='all', key='user_or_ip', rate='50/s', method=ALL, increment=True):
            raise Http404
        elif is_ratelimited(request, group='all', key='user_or_ip', rate='10000/d', method=ALL, increment=True):
            raise Http404
        else:
            return self.get_response(request)
