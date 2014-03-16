from django.test import TestCase
from tasks import test_task
from huey.djhuey import HUEY as huey
from huey.utils import EmptyData
import pickle

import datetime
from django.utils import timezone
from time import sleep


class TimezoneTestCase(TestCase):

    def test_utc(self):
        '''The Huey consumer needs to be running for this test.'''
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


