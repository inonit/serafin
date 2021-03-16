from __future__ import unicode_literals

from time import sleep

from django.test import TestCase
from django.db.models import signals

from system.engine import Engine
from system.models import Program, ProgramUserAccess, Session, Page, Email, SMS
from system.signals import *
from users.models import User, StatefulAnonymousUser


class EngineTestCase(TestCase):
    '''
    Test main methods for system.engine.Engine.
    Also indirectly tests some models and other classes the engine relies on.
    '''

    def setUp(self):
        # disable some signals
        signals.post_save.disconnect(schedule_sessions, sender=ProgramUserAccess)
        signals.pre_save.disconnect(session_pre_save, sender=Session)
        signals.post_save.disconnect(add_content_relations, sender=Session)
        signals.post_save.disconnect(schedule_session, sender=Session)
        signals.post_save.disconnect(content_post_save)

        # set up test user with save capability
        self.session = {}  # Django session, represented as simple dict
        self.user = StatefulAnonymousUser(session=self.session)
        self.user.data = {
            'session': 1,
            'node': 0,
            'email': 'tester@test.no',
            'phone': '+4799999999',
        }

        # set up a test program
        self.program = Program.objects.create(
            title='Program',
            display_title='Program'
        )

        # set up blank session
        self.session_empty = Session.objects.create(
            title='Empty session',
            display_title='Empty session',
            program=self.program,
            data={
                'nodes': [],
                'edges': []
            }
        )

        # set up some pages for a simple session
        self.page_first = Page.objects.create(
            title='First page',
            display_title='First page',
            content_type='page',
        )

        self.page_second = Page.objects.create(
            title='Second page',
            display_title='Second page',
            content_type='page',
        )

        # set up simple session
        self.session_simple = Session.objects.create(
            title='Simple session',
            display_title='Simple session',
            program=self.program,
            data={
                'nodes': [
                    {
                        'id': 0,
                        'type': 'start',
                        'title': 'Start',
                    },
                    {
                        'id': 1,
                        'type': 'page',
                        'title': self.page_first.title,
                        'ref_id': self.page_first.id,
                    },
                    {
                        'id': 2,
                        'type': 'page',
                        'title': self.page_second.title,
                        'ref_id': self.page_second.id,
                    },
                ],
                'edges': [
                    {
                        'type': 'normal',
                        'source': 0,
                        'target': 1,
                    },
                    {
                        'type': 'normal',
                        'source': 1,
                        'target': 2,
                    },
                ]
            }
        )

        # set up some content for a more complex session
        self.test_email = Email.objects.create(
            title='Test email',
            display_title='Test email',
            content_type='email',
            data=[{
                'content_type': 'text',
                'content': 'Email content'
            }]
        )

        self.test_sms = SMS.objects.create(
            title='Test sms',
            display_title='Test sms',
            content_type='sms',
            data=[{
                'content_type': 'text',
                'content': 'SMS content'
            }]
        )

        self.page_first_complex = Page.objects.create(
            title='First page complex',
            display_title='First page complex',
            content_type='page',
        )

        self.page_second_complex = Page.objects.create(
            title='Second page complex',
            display_title='Second page complex',
            content_type='page',
        )

        # set up complex session
        self.session_complex = Session.objects.create(
            title='Complex session',
            display_title='Complex session',
            program=self.program,
            data={
                'nodes': [
                    {
                        'id': 0,
                        'type': 'start',
                        'title': 'Start',
                    },
                    {
                        'id': 1,
                        'type': 'email',
                        'ref_id': self.test_email.id,
                        'title': 'Test epost',
                    },
                    {
                        'id': 2,
                        'type': 'sms',
                        'ref_id': self.test_sms.id,
                        'title': 'Test sms',
                    },
                    {
                        'id': 3,
                        'type': 'expression',
                        'variable_name': 'password',
                        'expression': '"hunter2"',
                    },
                    {
                        'id': 4,
                        'type': 'register',
                    },
                    {
                        'id': 5,
                        'type': 'enroll',
                    },
                    {
                        'id': 6,
                        'type': 'page',
                        'ref_id': self.page_first_complex.id,
                        'title': 'First page complex',
                    },
                    {
                        'id': 7,
                        'type': 'session',
                        'ref_id': self.session_simple.id,
                        'title': 'Simple session',
                    }
                ],
                'edges': [
                    # start to email, background
                    {
                        'id': 1,
                        'type': 'special',
                        'source': 0,
                        'target': 1,
                    },
                    # start to sms, background
                    {
                        'id': 2,
                        'type': 'special',
                        'source': 0,
                        'target': 2,
                    },
                    # start to expression
                    {
                        'id': 3,
                        'type': 'normal',
                        'source': 0,
                        'target': 3,
                    },
                    # expression to register
                    {
                        'id': 4,
                        'type': 'special',
                        'source': 3,
                        'target': 4,
                        'expression': '$password != None'
                    },
                    # register to enroll, if registered
                    {
                        'id': 5,
                        'type': 'special',
                        'source': 4,
                        'target': 5,
                        'expression': '$registered'
                    },
                    # enroll loop back to enrolled,
                    # long loop if enroll fails
                    {
                        'id': 6,
                        'type': 'special',
                        'source': 5,
                        'target': 5,
                        'expression': '$enrolled == False'
                    },
                    # expression to first page
                    {
                        'id': 7,
                        'type': 'normal',
                        'source': 3,
                        'target': 6,
                    },
                    # first page to simple session
                    {
                        'id': 8,
                        'type': 'normal',
                        'source': 6,
                        'target': 7,
                    }
                ]
            }
        )

        # set up processing session
        self.session_processing = Session.objects.create(
            title='Processing session',
            display_title='Processing session',
            program=self.program,
            data={
                'nodes': [
                    {
                        'id': 0,
                        'type': 'start',
                        'title': 'Start',
                    },
                    {
                        'id': 1,
                        'type': 'expression',
                        'variable_name': 'somevar',
                        'expression': '"some value"',
                    },
                ],
                'edges': [
                    {
                        'id': 1,
                        'type': 'normal',
                        'source': 0,
                        'target': 1,
                    },
                ]
            }
        )

        # set up hub session
        self.session_hub = Session.objects.create(
            title='Hub session',
            display_title='Hub session',
            program=self.program,
            data={
                'nodes': [
                    {
                        'id': 0,
                        'type': 'start',
                        'title': 'Start',
                    },
                    {
                        'id': 1,
                        'type': 'session',
                        'ref_id': self.session_processing.id,
                        'title': 'Simple session',
                    },
                    {
                        'id': 2,
                        'type': 'page',
                        'ref_id': self.page_first.id,
                        'title': 'First page',
                    },
                ],
                'edges': [
                    {
                        'id': 1,
                        'type': 'normal',
                        'source': 0,
                        'target': 1,
                    },
                    {
                        'id': 2,
                        'type': 'normal',
                        'source': 1,
                        'target': 2,
                    },
                ]
            }
        )


    def test_init(self):
        context = {
            'session': self.session_empty.id,
            'node': 0,
            'expression_somevar': '1 + 1',
            'other_var': 'value',
            'undefined': None,
        }
        engine = Engine(user=self.user, context=context)

        # test that user data is set (or not set) from context
        self.assertEqual(self.user.data['somevar'], 2)
        self.assertEqual(self.user.data['other_var'], 'value')
        self.assertEqual(self.user.data.get('undefined', 'no value'), 'no value')

        # test that session is loaded and initialized
        self.assertEqual(engine.session, self.session_empty)
        self.assertEqual(engine.nodes, {})
        self.assertEqual(engine.edges, [])

    def test_run(self):
        # test init with session and node context, a common pattern
        context = {
            'session': self.session_simple.id,
            'node': 0,
        }
        engine = Engine(user=self.user, context=context)

        self.assertEqual(engine.session, self.session_simple)
        self.assertEqual(self.user.data['node'], 0)

        # test run, will transition from start and return the first page
        page = engine.run()
        self.assertEqual(page, self.page_first)

        # repeated run will return the same page
        page = engine.run()
        self.assertEqual(page, self.page_first)

        # repeated run with next will return the second page
        engine = Engine(user=self.user)
        page = engine.run(next=True)
        self.assertEqual(page, self.page_second)
        self.assertEqual(self.user.data['session'], self.session_simple.id)
        self.assertEqual(self.user.data['node'], 2)

        # test init with push, will push current session and node to stack
        context = {
            'session': self.session_empty.id,
            'node': 0,
        }
        engine = Engine(user=self.user, context=context, push=True, is_interactive=True)
        self.assertEqual(engine.session, self.session_empty)
        self.assertEqual(self.user.data['node'], 0)
        self.assertEqual(self.user.data['stack'], [(self.session_simple.id, 2)])

        # run with pop will return to previous session and node
        engine.run(pop=True)
        self.assertEqual(engine.session, self.session_simple)
        self.assertEqual(self.user.data['session'], self.session_simple.id)
        self.assertEqual(self.user.data['node'], 2)

    def test_complex_session(self):
        context = {
            'session': self.session_complex.id,
            'node': 0,
        }
        engine = Engine(user=self.user, context=context)

        # retroactively monkey patch StatefulAnonymousUser
        def send_email(self, subject=None, message=None, html_message=None, **kwargs):

            self.data['mail'] = message
            self.save()

        def send_sms(self, message=None):

            self.data['sms'] = message
            self.save()

        StatefulAnonymousUser.send_email = send_email
        StatefulAnonymousUser.send_sms = send_sms

        # we expect this to cascade through a number of nodes
        page = engine.run()

        # having tried to send an email and sms (normally pass for StatefulAnonymousUser),
        # which we have monkey patched, saves to user data, which saves to session
        self.assertEqual(self.session['user_data']['mail'], 'Email content')
        self.assertEqual(self.session['user_data']['sms'], 'SMS content')

        # then registering the user,
        registered_user = engine.user
        self.assertIsNotNone(registered_user)
        self.assertFalse(registered_user.is_anonymous)

        # having set password for the user,
        self.assertTrue(registered_user.check_password('hunter2'))

        # then enrolled the user if registered,
        program_user = self.program.users.first()
        self.assertEqual(program_user, registered_user)

        # then not get stuck in an infinite loop on enroll,
        # then followed the normal edge from second expression to first page (asserted above)
        self.assertEqual(page, self.page_first_complex)

        # the next edge is a session node, should return the first page of that node
        engine = Engine(user=self.user)
        page = engine.run(next=True)
        self.assertEqual(page, self.page_first)

    def test_snippet(self):
        # re-init user
        self.session = {}
        self.user = StatefulAnonymousUser(session=self.session)
        self.user.data = {}

        context = {
            'session': self.session_hub.id,
            'node': 0,
        }
        engine = Engine(user=self.user, context=context)
        page = engine.run()

        # we've visited processing session and set value
        self.assertEqual(self.user.data['somevar'], 'some value')

        # stack is now empty
        self.assertEqual(self.user.data['stack'], [])

        # we're on page_first
        self.assertEqual(page, self.page_first)
