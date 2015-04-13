from django.contrib import auth
from django.utils.functional import SimpleLazyObject


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


class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))
