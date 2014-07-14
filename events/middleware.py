from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

import json
from django.conf import settings
from django.utils import timezone
from events.models import Event


class EventTrackingMiddleware(object):
    '''Tracks and logs user data and page visits'''

    def process_request(self, request):

        if (request.is_ajax() and
            request.method == 'POST' and
            not request.user.is_anonymous() and
            not request.FILES and
            getattr(
                settings, 'LOG_AJAX_USER_DATA', False
            )
        ):
            try:
                post_data = json.loads(request.body)
                for item in post_data:
                    key = item.get('key', '')
                    pre_value = request.user.data.get(key, '')
                    post_value = item.get('value', '')

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
            except:
                pass

        if request.is_ajax() and not getattr(
            settings, 'LOG_AJAX_REQUESTS', False
        ):
            return

        if request.user.is_anonymous() and not getattr(
            settings, 'LOG_ANONYMOUS_REQUESTS', False
        ):
            return

        if request.user.is_superuser and not getattr(
            settings, 'LOG_ADMIN_REQUESTS', False
        ):
            return

        if getattr(
            settings, 'LOG_REQUESTS', False
        ):
            device = _('Other')
            if request.user_agent.is_mobile:
                device = _('Mobile')
            elif request.user_agent.is_tablet:
                device = _('Tablet')
            elif request.user_agent.is_pc:
                device = _('PC')

            summary = '%s, %s %s %s' % (
                device,
                request.user_agent.device.family,
                request.user_agent.os.family,
                request.user_agent.os.version_string,
            )

            req = '%s %s' % (
                request.method,
                request.path,
            )

            event = Event(
                time=timezone.localtime(timezone.now()),
                domain='request',
                actor=request.user,
                variable=req,
                pre_value='',
                post_value=summary,
            )
            event.save()
