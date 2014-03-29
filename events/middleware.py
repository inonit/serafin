from __future__ import unicode_literals

from django.conf import settings

from .models import Event


class EventTrackingMiddleware(object):
    ''' Tracks and logs user page visits and their time spent '''

    def process_response(self, request, response):

        # Check for ajax requests
        if request.is_ajax() and not settings.TRACK_AJAX_REQUESTS:
            return response

        user = getattr(request, 'user', None)
        # Check for anonymous users
        if not user or user.is_anonymous():
            if not settings.TRACK_ANONYMOUS_USERS:
                return response
            user = None

        # Check for admin users
        if user and user.is_superuser:
            if not settings.TRACK_ADMIN_USERS:
                return response

        # Logs an event
        Event.objects.create_event(
            domain=request.path,
            actor=user,
            variable='',
            pre_value='',
            post_value=''
        )

        return response