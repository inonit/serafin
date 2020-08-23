from django.conf import settings
from django.db.models import Q

from system.models import ChatMessage


def add_support_email(request):
    if request.user.is_authenticated:
        return {'support_email': settings.SUPPORT_EMAIL}
    return {}


def add_basic_user_info(request):
    if not request.user.is_authenticated:
        return {}

    has_therapist = request.user.therapist is not None
    has_unread_messages = False
    if has_therapist:
        has_unread_messages = ChatMessage.objects.filter(Q(sender=request.user.therapist) & Q(receiver=request.user)
                                                         & Q(is_read=False)).count() > 0
    return {
        'has_therapist': has_therapist,
        'email': request.user.email,
        'has_message': has_unread_messages
    }
