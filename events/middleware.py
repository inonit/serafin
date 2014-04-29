from __future__ import unicode_literals

from django.conf import settings

from events.models import Event


class EventTrackingMiddleware(object):
    '''Tracks and logs user page visits'''

    def process_response(self, request, response):

        if request.is_ajax() and not settings.TRACK_AJAX_REQUESTS:
            return response

        if request.user.is_anonymous() and not settings.TRACK_ANONYMOUS_USERS:
            return response

        if request.user.is_superuser and not settings.TRACK_ADMIN_USERS:
            return response

        device = 'other'
        if user_agent.is_mobile:
            device = 'mobile'
        elif user_agent.is_tablet:
            device = 'tablet'
        elif user_agent.is_pc:
            device = 'pc'

        summary = '%s %s %s' % (
            request.user_agent.device.family,
            request.user_agent.os.family,
            request.user_agent.os.version_string,
        )

        req = '%s %s' % (
            request.method,
            request.path_info,
        )

        Event.objects.create_event(
            domain=request.path,
            actor=user,
            variable='device',
            pre_value='',
            post_value=device,
        )

        return response
