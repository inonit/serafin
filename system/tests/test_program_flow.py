from __future__ import unicode_literals

from time import sleep
from collections import namedtuple

from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase
from django.db.models import signals

from system.engine import Engine
from system.models import Program, ProgramUserAccess, Session, Page, Email, SMS
from system.signals import *
from users.models import User, StatefulAnonymousUser
from users.views import receive_sms
from tokens.tokens import token_generator

import json


class ProgramFlowTestCase(TestCase):
    '''
    Test a setup based on SERAFs Endre program flow.
    '''

    def setUp(self):
        # disable some signals
        signals.post_save.disconnect(schedule_sessions, sender=ProgramUserAccess)
        signals.pre_save.disconnect(session_pre_save, sender=Session)
        signals.post_save.disconnect(add_content_relations, sender=Session)
        signals.post_save.disconnect(schedule_session, sender=Session)
        signals.post_save.disconnect(content_post_save)

        # set up a test program
        self.program = Program.objects.create(
            title='Program',
            display_title='Program'
        )

        # set up page for lapse session
        self.page_lapse = Page.objects.create(
            title='Second page',
            display_title='Second page',
            content_type='page',
        )

        # set up 'LapseSession' session
        self.session_lapse_session = Session.objects.create(
            title='EndreFlow LapseSession',
            display_title='EndreFlow LapseSession',
            program=self.program,
            data={
                "nodes": [
                    {
                        "id": 0,
                        "type": "start",
                        "title": "Start",
                    },
                    {
                        "id": 1,
                        "type": "page",
                        "ref_id": self.page_lapse.id,
                        "title": self.page_lapse.title,
                    }
                ],
                "edges": [
                    {
                        "id": 1,
                        "type": "normal",
                        "source": 0,
                        "target": 1,
                    }
                ]
            }
        )

        self.sms_question = SMS.objects.create(
            title='EndreFlow SMS Question',
            display_title='EndreFlow SMS Question',
            content_type='sms',
            data=[{
                'content_type': 'text',
                'content': 'SMS content'
            }]
        )

        self.sms_lapse = SMS.objects.create(
            title='EndreFlow SMS Lapse',
            display_title='EndreFlow SMS Lapse',
            content_type='sms',
            data=[{
                'content_type': 'text',
                'content': 'SMS content'
            }]
        )

        self.sms_ok = SMS.objects.create(
            title='EndreFlow SMS OK',
            display_title='EndreFlow SMS OK',
            content_type='sms',
            data=[{
                'content_type': 'text',
                'content': 'SMS content'
            }]
        )

        # set up 'Lapse' session
        self.session_lapse = Session.objects.create(
            title='EndreFlow Lapse',
            display_title='EndreFlow Lapse',
            program=self.program,
            data={
                "nodes": [
                    {
                        "id": 0,
                        "type": "start",
                        "title": "Start",
                    },
                    {
                        "id": 1,
                        "type": "expression",
                        "expression": "entered lapse",
                        "variable_name": "testFlowA",
                    },
                    {
                        "id": 2,
                        "type": "delay",
                        "delay": {
                            "number": 1,
                            "unit": "minutes"
                        },
                    },
                    {
                        "id": 3,
                        "type": "sms",
                        "ref_id": self.sms_question.id,
                        "title": self.sms_question.title,
                    },
                    {
                        "id": 5,
                        "type": "expression",
                        "expression": "lapse",
                        "variable_name": "testFlowA",
                    },
                    {
                        "id": 6,
                        "type": "session",
                        "ref_id": self.session_lapse_session.id,
                        "title": self.session_lapse_session.title,
                    },
                    {
                        "id": 7,
                        "type": "sms",
                        "ref_id": self.sms_lapse.id,
                        "title": self.sms_lapse.title,
                    },
                    {
                        "id": 8,
                        "type": "sms",
                        "ref_id": self.sms_ok.id,
                        "title": self.sms_ok.title,
                    },
                    {
                        "id": 9,
                        "type": "expression",
                        "expression": "no lapse",
                        "variable_name": "testFlowA",
                    }
                ],
                "edges": [
                    {
                        "id": 1,
                        "type": "special",
                        "source": 0,
                        "target": 1,
                    },
                    {
                        "id": 5,
                        "type": "normal",
                        "source": 5,
                        "target": 6,
                    },
                    {
                        "id": 6,
                        "type": "special",
                        "source": 1,
                        "target": 2,
                    },
                    {
                        "id": 7,
                        "type": "special",
                        "source": 2,
                        "target": 3,
                    },
                    {
                        "id": 8,
                        "type": "special",
                        "source": 3,
                        "target": 8,
                        "expression": "'no' in $testFlowB"
                    },
                    {
                        "id": 9,
                        "type": "special",
                        "source": 3,
                        "target": 7,
                        "expression": "'yes' in $testFlowB"
                    },
                    {
                        "id": 10,
                        "type": "special",
                        "source": 7,
                        "target": 5,
                    },
                    {
                        "id": 11,
                        "type": "special",
                        "source": 8,
                        "target": 9,
                    }
                ]
            }
        )

        # set up page for non-lapse
        self.page_session = Page.objects.create(
            title='First page',
            display_title='First page',
            content_type='page',
        )

        # set up 'Session' session
        self.session_session = Session.objects.create(
            title='EndreFlow Session',
            display_title='EndreFlow Session',
            program=self.program,
            data={
                "nodes": [
                    {
                        "id": 0,
                        "type": "start",
                        "title": "Start",
                    },
                    {
                        "id": 1,
                        "type": "page",
                        "ref_id": self.page_session.id,
                        "title": self.page_session.title,
                    }
                ],
                "edges": [
                    {
                        "id": 1,
                        "type": "normal",
                        "source": 0,
                        "target": 1,
                    }
                ]
            }
        )

        # set up 'Executive' session
        self.session_executive = Session.objects.create(
            title='EndreFlow Executive',
            display_title='EndreFlow Executive',
            program=self.program,
            data={
                "nodes": [
                    {
                        "id": 0,
                        "type": "start",
                        "title": "Start",
                    },
                    {
                        "id": 1,
                        "type": "session",
                        "ref_id": self.session_lapse.id,
                        "title": self.session_lapse.title,
                    },
                    {
                        "id": 2,
                        "type": "expression",
                        "expression": "passed lapse",
                        "variable_name": "testFlowC",
                    },
                    {
                        "id": 3,
                        "type": "session",
                        "ref_id": self.session_session.id,
                        "title": self.session_session.title,
                    }
                ],
                "edges": [
                    {
                        "id": 1,
                        "type": "normal",
                        "source": 0,
                        "target": 1,
                    },
                    {
                        "id": 2,
                        "type": "special",
                        "source": 1,
                        "target": 2,
                    },
                    {
                        "id": 3,
                        "type": "normal",
                        "source": 2,
                        "target": 3,
                    }
                ]
            }
        )

        # set up 'Activate' session
        self.session_activate = Session.objects.create(
            title='EndreFlow Activate',
            display_title='EndreFlow Activate',
            program=self.program,
            data={
                "nodes": [
                    {
                        "id": 0,
                        "type": "start",
                        "title": "Start",
                    },
                    {
                        "id": 1,
                        "type": "session",
                        "ref_id": self.session_executive.id,
                        "title": self.session_executive.title,
                    }
                ],
                "edges": [
                    {
                        "id": 1,
                        "type": "normal",
                        "source": 0,
                        "target": 1,
                    }
                ]
            }
        )

        self.user = User()
        self.user.save()

        # add user to program
        self.programuseraccess = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user,
            time_factor=0.01
        )

    def test_flow(self):
        # test init with session and node context, a common pattern
        context = {
            'session': self.session_activate.id,
            'node': 0,
        }
        engine = Engine(user=self.user, context=context)
        self.assertEqual(engine.session, self.session_activate)
        page = engine.run()

        token = token_generator.make_token(self.user.id)
        default_data = {
            'From': '+4799999999',
            'Body': 'no',
        }

        primafon_data = {
            'from': '4799999999',
            'body': 'no',
        }

        Request = namedtuple('Request', 'method body POST')
        request = Request(
            method='POST',
            body=json.dumps(primafon_data),
            POST=default_data
        )
        receive_sms(request)
