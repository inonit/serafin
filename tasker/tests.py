from __future__ import print_function
import datetime
import pickle
from time import sleep

from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import TestCase, modify_settings
from django.utils import timezone

from huey.contrib.djhuey import HUEY as huey, task
from huey.constants import EmptyData

from tasker.models import Task
from system.models import Program, ProgramUserAccess, Session
from system.signals import *

User = get_user_model()


@huey.task()
def gal_task():
    return "GAL TASK"


@huey.task()
def test_task():
    message = 'Hello Huey!'
    return message


class TimezoneTestCase(TestCase):
    '''
    Huey operates on UTC time, which may not be the case for
    Django or the system it's running on.

    This tests that the employed strategy for normalizing time
    works as intended.

    The Huey consumer needs to be running for this test.
    '''

    def test_utc(self):

        d1 = timezone.now()
        d2 = timezone.now() + datetime.timedelta(minutes=1)

        task1 = test_task.schedule(
            eta=timezone.localtime(d1).replace(tzinfo=None)
        )
        task2 = test_task.schedule(
            eta=timezone.localtime(d2).replace(tzinfo=None)
        )

        sleep(5)

        result1 = task1()
        result2 = task2()

        self.assertNotEqual(result1, result2)


class TaskerTestCase(TestCase):
    '''
    This tests creating, revoking and rescheduling tasks using
    the Task model.

    The Huey consumer needs to be running for these tests.
    '''

    def setUp(self):
        self.program = Program(title='Program', display_title='Program')
        self.program.save()

        self.user = User.objects.create_user(1, 'test', 'test@test.no', '98765432')
        self.user.save()

    def test_create_task(self):
        '''Test direct task creation'''

        task = Task.objects.create_task(
            sender=self.program,
            domain='domain',
            time=timezone.localtime(timezone.now()),
            task=test_task,
            args=None,
            action='action',
            subject=self.user
        )

        sleep(2)

        # check result is returned
        self.assertEqual(task.result, 'Hello Huey!')

        # check result is still the same
        self.assertEqual(task.result, 'Hello Huey!')

        print('test_create_task task id: %s' % task.task_id)

        task = Task.objects.create_task(
            sender=self.program,
            domain='domain',
            time=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=1),
            task=test_task,
            args=None,
            action='action',
            subject=self.user
        )

        sleep(2)

        # future task should have no result
        self.assertEqual(task.result, None)

        print('test_create_task (future) task id: %s' % task.task_id)

    def test_reschedule_past_task(self):
        '''Test direct task rescheduling with task in the past'''

        task = Task.objects.create_task(
            sender=self.program,
            domain='domain',
            time=timezone.localtime(timezone.now()) - datetime.timedelta(minutes=1),
            task=test_task,
            args=None,
            action='action',
            subject=self.user
        )

        sleep(2)

        self.assertEqual(task.result, 'Hello Huey!')

        task.reschedule(test_task, None, timezone.localtime(timezone.now()) + datetime.timedelta(seconds=1))

        # shows how reschedule works: task has already run,
        # but loses result...
        self.assertIs(task.result, None)

        sleep(5)

        # ...and will run again on new schedule
        self.assertEqual(task.result, 'Hello Huey!')

        print('test_reschedule_past_task task id: %s' % task.task_id)

    def test_reschedule_future_task(self):
        '''Test direct task rescheduling with task in the future'''

        task = Task.objects.create_task(
            sender=self.program,
            domain='domain',
            time=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=1),
            task=test_task,
            args=None,
            action='action',
            subject=self.user
        )
        task.reschedule(test_task, None, timezone.localtime(timezone.now()))

        sleep(2)

        # future task should be rescheduled and run, so it should have a result
        self.assertEqual(task.result, 'Hello Huey!')

        print('test_reschedule_future_task task id: %s' % task.task_id)

    def test_revoke_task(self):
        '''Test direct task revocation'''

        task = Task.objects.create_task(
            sender=self.program,
            domain='domain',
            time=timezone.localtime(timezone.now()) + datetime.timedelta(seconds=1),
            task=test_task,
            args=None,
            action='action',
            subject=self.user
        )
        task.revoke()

        sleep(5)

        # task was revoked before run, so it should have no result
        self.assertIs(task.result, None)

        print('test_revoke_task task id: %s' % task.task_id)


class SessionIntegrationTestCase(TestCase):
    '''
    This tests predicted indirect Task creation, revocation and rescheduling
    by signal receivers when manipulating Session and ProgramUserAccess models.

    The Huey consumer needs to be running for these tests.
    '''

    def setUp(self):
        signals.post_save.connect(schedule_sessions, sender=ProgramUserAccess)
        signals.pre_save.connect(session_pre_save, sender=Session)
        signals.post_save.connect(add_content_relations, sender=Session)
        signals.post_save.connect(schedule_session, sender=Session)
        signals.post_save.connect(content_post_save)

        self.program = Program(title='Program', display_title='Program')
        self.program.save()

        self.user_a = User.objects.create_user(1, 'test', 'test1@test.no', '98765431')
        self.user_a.save()

        self.user_b = User.objects.create_user(2, 'test', 'test2@test.no', '98765432')
        self.user_b.save()

    def test_schedule_sessions(self):
        '''Test session task scheduling with receiver for ProgramUserAccess post_save'''

        # will signal schedule_session,
        # but no ProgramUserAccess is in session.program.programuseraccess_set
        session = Session.objects.create(
            title='Empty session',
            display_title='Empty session',
            program=self.program,
            scheduled=True,
            data={
                'nodes': [],
                'edges': []
            }
        )

        # receiver schedule_sessions will create a task on post_save
        useraccess_a = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_a,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(seconds=1),
        )

        # find the Task just created by receiver,
        # reschedule to the same time so we can swap init_session with test_task,
        # save the Task
        task_a = Task.objects.latest('pk')
        task_a.reschedule(task=test_task, args=None, time=task_a.time)
        task_a.save()

        # see above
        useraccess_b = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_b,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=1),
        )

        # see above
        task_b = Task.objects.latest('pk')
        task_b.reschedule(task=test_task, args=None, time=task_b.time)
        task_b.save()

        sleep(5)

        # task_a should have run and have a result
        self.assertEqual(task_a.result, 'Hello Huey!')
        # task_b should not have run have result None
        self.assertIs(task_b.result, None)

    def test_schedule_session(self):
        '''Test session task scheduling with receiver for Session post_save'''

        # will signal schedule_sessions (see test_schedule_sessions),
        # but no Session is in useraccess.program.session_set
        useraccess_a = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_a,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(seconds=1),
        )

        # see above
        useraccess_b = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_b,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=1),
        )

        # will schedule session for both users
        session = Session.objects.create(
            title='Empty session',
            display_title='Empty session',
            program=self.program,
            scheduled=True,
            data={
                'nodes': [],
                'edges': []
            }
        )

        # next last Task created should correspond to useraccess_a
        task_a = list(Task.objects.all())[-2]
        task_b = list(Task.objects.all())[-1]
        task_a.reschedule(task=test_task, args=None, time=task_a.time)
        task_a.save()

        # last Task created should correspond to useraccess_b
        task_b.reschedule(task=test_task, args=None, time=task_b.time)
        task_b.save()

        sleep(5)

        # task_a should have run and have a result
        self.assertEqual(task_a.result, 'Hello Huey!')
        # task_b should not have run have result None
        self.assertIs(task_b.result, None)

    def test_reschedule_session(self):
        '''Test session task rescheduling with receiver for Session post_save'''

        # see test_schedule_session
        useraccess_a = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_a,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(seconds=1),
        )

        # see test_schedule_session
        useraccess_b = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_b,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=1),
        )

        # will schedule session for both users
        session = Session.objects.create(
            title='Empty session',
            display_title='Empty session',
            program=self.program,
            scheduled=True,
            data={
                'nodes': [],
                'edges': []
            }
        )

        # re-save session to trigger reschedule_session
        session.save()

        # swap task function for user_a
        task_a = list(Task.objects.all())[-2]
        task_b = list(Task.objects.all())[-1]
        task_a.reschedule(task=test_task, args=None, time=task_a.time)
        task_a.save()

        # swap task function for user_b
        task_b.reschedule(task=test_task, args=None, time=task_b.time)
        task_b.save()

        sleep(5)

        # task_a should have run and have a result
        self.assertEqual(task_a.result, 'Hello Huey!')
        # task_b should not have run have result None
        self.assertIs(task_b.result, None)

    def test_revoke_session(self):
        '''Test session task revoke with receiver for Session pre_delete'''

        # see test_schedule_session
        useraccess_a = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_a,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(seconds=1),
        )

        # see test_schedule_session
        useraccess_b = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_b,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=1),
        )

        # get last task before scheduling
        try:
            last_task_before = Task.objects.latest('pk')
        except Task.DoesNotExist:
            last_task_before = None

        # will schedule session for both users
        session = Session.objects.create(
            title='Empty session',
            display_title='Empty session',
            program=self.program,
            scheduled=True,
            data={
                'nodes': [],
                'edges': []
            }
        )

        # re-save session to trigger reschedule_session
        session.delete()

        # get last task after deleting session
        try:
            last_task_after = Task.objects.latest('pk')
        except Task.DoesNotExist:
            last_task_after = None

        # last task should be same before and after deleting,
        # i.e. session.delete() also deleted the tasks connected to it
        self.assertIs(last_task_before, last_task_after)

    def test_revoke_tasks(self):
        '''Test session task revoke with receiver for ProgramUserAccess pre_delete'''

        # see test_schedule_sessions
        session = Session.objects.create(
            title='Empty session',
            display_title='Empty session',
            program=self.program,
            scheduled=True,
            data={
                'nodes': [],
                'edges': []
            }
        )

        # get last task before scheduling
        try:
            last_task_before = Task.objects.latest('pk')
        except Task.DoesNotExist:
            last_task_before = None

        # receiver schedule_sessions will create a task on post_save
        useraccess = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_a,
            start_time=timezone.localtime(timezone.now()) + datetime.timedelta(seconds=1),
        )

        useraccess.delete()

        # get last task after deleting programuseraccess
        try:
            last_task_after = Task.objects.latest('pk')
        except Task.DoesNotExist:
            last_task_after = None

        # last task should be same before and after deleting,
        # i.e. useraccess.delete() also deleted the tasks connected to it
        self.assertIs(last_task_before, last_task_after)

    def test_schedule_sessions_with_time_factor(self):
        '''Test session task scheduling with variable time factors'''

        session = Session.objects.create(
            title='Empty session',
            display_title='Empty session',
            program=self.program,
            scheduled=True,
            start_time_delta=1,
            start_time_unit='minutes',
            data={
                'nodes': [],
                'edges': []
            }
        )

        now = timezone.localtime(timezone.now())

        # add a useraccess with normal time_factor
        useraccess_a = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_a,
            start_time=now,
            time_factor=1.0,
        )

        task_time = session.get_start_time(
            useraccess_a.start_time,
            useraccess_a.time_factor
        )

        task_a = Task.objects.latest('pk')
        task_a.reschedule(task=test_task, args=None, time=task_time)
        task_a.save()

        # add a useraccess with accelerated time_factor
        useraccess_b = ProgramUserAccess.objects.create(
            program=self.program,
            user=self.user_b,
            start_time=now,
            time_factor=0.001,
        )

        task_time = session.get_start_time(
            useraccess_b.start_time,
            useraccess_b.time_factor
        )

        task_b = Task.objects.latest('pk')
        task_b.reschedule(task=test_task, args=None, time=task_time)
        task_b.save()

        sleep(5)

        # task_a should not have run have result None
        self.assertIs(task_a.result, None)
        # task_b was accelerated, should have run and have a result
        self.assertEqual(task_b.result, 'Hello Huey!')
