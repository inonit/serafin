from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

import json
from django.conf import settings
from django.utils import timezone
from events.models import Event


class EventTrackingMiddleware(object):
    '''Tracks and logs time spent on page and user data'''

    def process_request(self, request):

        try:
            request_body = json.loads(request.body)
        except:
            request_body = {}

        timer = request_body.get('timer')
        if timer:
            del request_body['timer']

        request._body = json.dumps(request_body)

        if getattr(settings, 'LOG_TIME_PER_PAGE', False) and timer:

            max_time = getattr(settings, 'LOG_MAX_MILLISECONDS', 0)
            if max_time:
                timer = min((timer, max_time))

            event = Event(
                time=timezone.localtime(timezone.now()),
                domain='userdata',
                actor=request.user,
                variable='timer',
                pre_value='',
                post_value=unicode(timer),
            )
            event.save()

        if (request.is_ajax() and
            request.method == 'POST' and
            not request.user.is_anonymous() and
            not request.FILES and
            getattr(settings, 'LOG_USER_DATA', False)
        ):
            for key, post_value in request_body.items():

                pre_value = request.user.data.get(key, '')

                if isinstance(pre_value, list):
                    pre_value = ', '.join([v.strip() for v in pre_value])

                if isinstance(post_value, list):
                    post_value = ', '.join([v.strip() for v in post_value])

                event = Event(
                    time=timezone.localtime(timezone.now()),
                    domain='userdata',
                    actor=request.user,
                    variable=key,
                    pre_value=unicode(pre_value),
                    post_value=unicode(post_value),
                )
                event.save()
