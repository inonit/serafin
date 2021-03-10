from django.conf import settings
from django.db.models import Q



def add_support_email(request):
    if request.user.is_authenticated:
        return {'support_email': settings.SUPPORT_EMAIL}
    return {}


