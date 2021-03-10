from __future__ import unicode_literals
from builtins import str
from builtins import object
from django.utils.translation import ugettext_lazy as _
from django.utils.deprecation import MiddlewareMixin

import json
from django.conf import settings
from django.utils import timezone
from events.models import Event
from system.models import Session


class EventTrackingMiddleware(MiddlewareMixin):
    '''Tracks and logs time spent on page and user data'''

    def process_request(self, request):

        if (not request.is_ajax() or
                not request.method == 'POST' or
                request.FILES or
                request.user.is_anonymous or
                'api/system' in request.path or
                'api/users' in request.path):
            return

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

            try:
                session_id = request.user.data.get('session')
                node_id = request.user.data.get('node')

                session = Session.objects.get(id=session_id)
                nodes = {node['id']: node for node in session.data.get('nodes')}

                title = nodes[node_id]['title']
            except:
                title = ''

            event = Event(
                time=timezone.localtime(timezone.now()),
                domain='userdata',
                actor=request.user,
                variable='timer',
                pre_value='',
                post_value='%s, %s ms' % (title, timer),
            )
            event.save()

        if getattr(settings, 'LOG_USER_DATA', False):

            for key, post_value in list(request_body.items()):

                if key in ['email', 'phone', 'password']:
                    continue

                def recursive_stripe(v):
                    if isinstance(v, list):
                        return '[' + ', '.join([recursive_stripe(x) for x in v]) + ']'
                    else:
                        return v.strip()

                pre_value = request.user.get_pre_variable_value_for_log(key)

                if isinstance(post_value, list):
                    post_value = ', '.join([recursive_stripe(v) for v in post_value])

                event = Event(
                    time=timezone.localtime(timezone.now()),
                    domain='userdata',
                    actor=request.user,
                    variable=key,
                    pre_value=str(pre_value),
                    post_value=str(post_value),
                )
                event.save()
