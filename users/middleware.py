from django.contrib import auth
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import AuthenticationMiddleware

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
        if request.user.is_authenticated:
            session_id = request.user.data.get('session')
            try:
                session = get_object_or_404(Session, id=session_id)
                if session and session.program and session.program.is_rtl:
                    translation.activate('he')
            except Http404 as ex:
                pass

