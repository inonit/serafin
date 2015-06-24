import datetime
import pickle
from time import sleep

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import signals
from django.test import TestCase
from django.utils import timezone

from huey.djhuey import HUEY as huey, task
from huey.utils import EmptyData

from tasker.models import Task
from system.models import Program, ProgramUserAccess, Session
from users.signals import mirror_user


User = get_user_model()


@task()
def test_task():
    message = 'Hello Huey!'

    print message
    return message


class TimezoneTestCase(TestCase):
    '''The Huey consumer needs to be running for these tests'''

    def test_utc(self):

        d1 = timezone.now()
        d2 = timezone.now() + datetime.timedelta(minutes=1)

        task1 = test_task.schedule(
            eta=timezone.localtime(d1).replace(tzinfo=None),
            convert_utc=False
        )
        task2 = test_task.schedule(
            eta=timezone.localtime(d2).replace(tzinfo=None),
            convert_utc=False
        )

        sleep(2)

        result1 = huey._get(task1.task.task_id, peek=True)
        if result1 is not EmptyData:
            result1 = pickle.loads(result1)

        result2 = huey._get(task2.task.task_id, peek=True)
        if result2 is not EmptyData:
            result2 = pickle.loads(result2)

        self.assertNotEqual(result1, result2)


class TaskerTestCase(TestCase):
    '''The Huey consumer needs to be running for these tests.'''

    def setUp(self):
        # if using users.User, disable signal to mirror user
        signals.post_save.disconnect(mirror_user, sender=User)

        self.program = Program(title='Program', display_title='Program')
        self.program.save()

        self.user = User.objects.create_user('test', password='test')
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

        sleep(0.25)

        # check result is returned
        self.assertEqual(task.result, 'Hello Huey!')

        # check result is still the same
        self.assertEqual(task.result, 'Hello Huey!')

        print 'test_create_task task id: %s' % task.task_id

        task = Task.objects.create_task(
            sender=self.program,
            domain='domain',
            time=timezone.localtime(timezone.now()) + datetime.timedelta(minutes=1),
            task=test_task,
            args=None,
            action='action',
            subject=self.user
        )

        sleep(0.25)

        # future task should have no result
        self.assertEqual(task.result, None)

        print 'test_create_task (future) task id: %s' % task.task_id

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

        sleep(0.25)

        self.assertEqual(task.result, 'Hello Huey!')

        task.reschedule(test_task, None, timezone.localtime(timezone.now()) + datetime.timedelta(seconds=1))

        # shows how reschedule works: task has already run,
        # but loses result...
        self.assertIs(task.result, None)

        sleep(2)

        # ...and will run again on new schedule
        self.assertEqual(task.result, 'Hello Huey!')

        print 'test_reschedule_past_task task id: %s' % task.task_id

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

        sleep(0.25)

        # future task should be rescheduled and run, so it should have a result
        self.assertEqual(task.result, 'Hello Huey!')

        print 'test_reschedule_future_task task id: %s' % task.task_id

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

        sleep(2)

        # task was revoked before run, so it should have no result
        self.assertIs(task.result, None)

        print 'test_revoke_task task id: %s' % task.task_id

