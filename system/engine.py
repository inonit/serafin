# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from events.signals import log_event
from system.models import Variable, Session, Page, Email, SMS
from tasker.models import Task
from .expressions import Parser


class EngineException(Exception):
    pass


class Engine(object):
    '''A simplified decision engine to traverse the Session graph for a user'''

    def __init__(self, user=None, user_id=None, context={}, push=False):
        '''
        Initialize Engine with a User or user id and optional context.

        The argument user accepts a user instance, which gives support for
        unconventional user models (e.g. users.StatefulAnonymousUser) or when
        user is known.

        User id should be used for tasks, which should not have complex types.

        If argument push is True, current session and node will be pushed to
        a stack, so the user may return there.
        '''

        if user:
            self.user = user
        else:
            self.user = get_user_model().objects.get(id=user_id)

        # push current session and node to stack if entering subsession
        if push:

            session = self.user.data.get('session')
            node = self.user.data.get('node')

            if session and node is not None:
                stack = self.user.data.get('stack', [])
                stack.append((session, node))
                self.user.data['stack'] = stack

        # process context if available
        if context:

            for key, value in context.items():

                if 'expression_' in key:
                    try:
                        parser = Parser(user_obj=self.user)
                        value = parser.parse(value)
                    except:
                        pass

                    parts = key.split('_')[1:]
                    key = ''.join(parts)

                    self.user.data[key] = value

                elif key and value is not None:
                    self.user.data[key] = value

        # save
        if push or context:
            self.user.save()

        self.init_session()

    def init_session(self, session_id=None, node_id=None):

        session_id = session_id or self.user.data.get('session')
        if node_id is None:
            node_id = self.user.data.get('node')

        self.user.data['session'] = session_id
        self.user.data['node'] = node_id
        self.user.save()

        self.session = Session.objects.get(id=session_id)

        self.nodes = {node['id']: node for node in self.session.data.get('nodes')}
        self.edges = self.session.data.get('edges')

    def get_node_edges(self, source_id):
        return [edge for edge in self.edges if edge.get('source') == source_id]

    def get_normal_edges(self, edges):
        return [edge for edge in edges if edge.get('type') == 'normal']

    def get_special_edges(self, edges):
        return [edge for edge in edges if edge.get('type') == 'special']

    def is_stacked(self):
        '''Check if current session has sessions below in stack'''

        return bool(self.user.data.get('stack'))

    def is_dead_end(self, node_id):
        '''Check if current node is a dead end (end of session)'''

        target_edges = self.get_node_edges(node_id)
        normal_edges = self.get_normal_edges(target_edges)
        return len(normal_edges) == 0

    def handle_dead_end(self, node_id):
        '''Resolve a background processed dead end'''

        if self.is_dead_end(node_id) and self.is_stacked():

            node = self.nodes.get(node_id)
            if node.get('type') in ['start', 'session', 'expression']:

                return self.run(pop=True)

    def traverse(self, edges, source_id):
        '''Select and return first edge where the user passes edge conditions'''

        for edge in edges:
            expression = edge.get('expression')

            if expression:
                try:
                    parser = Parser(user_obj=self.user)
                    passed = parser.parse(expression)
                except:
                    passed = False

                if passed:
                    return edge
            else:
                return edge

    def transition(self, source_id):
        '''Transition from a given node and trigger a new node'''

        edges = self.get_node_edges(source_id)

        special_edges = self.get_special_edges(edges)
        normal_edges = self.get_normal_edges(edges)

        # traverse all special edges
        while special_edges:
            edge = self.traverse(special_edges, source_id)

            if edge:
                target_id = edge.get('target')
                special_edges.remove(edge)
                self.trigger_node(target_id)
            else:
                break

        # traverse first applicable normal edge
        edge = self.traverse(normal_edges, source_id)

        if edge:
            target_id = edge.get('target')
            return self.trigger_node(target_id)
        else:
            return self.handle_dead_end(source_id)

    def trigger_node(self, node_id):
        '''Trigger action for a given node, return if Page'''

        node = self.nodes.get(node_id)
        node_type = node.get('type')
        ref_id = node.get('ref_id')

        if node_type == 'start':
            return self.transition(node_id)

        if node_type == 'page':
            page = Page.objects.get(id=ref_id)
            page.update_html(self.user)

            page.dead_end = self.is_dead_end(node_id)
            page.stacked = self.is_stacked()

            log_event.send(
                self,
                domain='session',
                actor=self.user,
                variable='transition',
                pre_value=self.nodes[self.user.data['node']]['title'],
                post_value=page.title
            )

            self.user.data['node'] = node_id
            self.user.save()

            return page

        if node_type == 'session':

            if self.is_dead_end(node_id):
                self.user.data['stack'] = []
            else:
                stack = self.user.data.get('stack', [])
                stack.append((self.session.id, node_id))
                self.user.data['stack'] = stack

            self.init_session(ref_id, 0)

            return self.transition(0)

        if node_type == 'expression':
            expression = node.get('expression')
            variable_name = node.get('variable_name')

            if expression:
                try:
                    parser = Parser(user_obj=self.user)
                    result = parser.parse(expression)
                except:
                    result = None

                if variable_name:
                    self.user.data[variable_name] = result
                    self.user.save()

            return self.transition(node_id)

        if node_type == 'email':
            email = Email.objects.get(id=ref_id)
            email.send(self.user)

            log_event.send(
                self,
                domain='session',
                actor=self.user,
                variable='email',
                pre_value='',
                post_value=email.title
            )

            self.transition(node_id)

        if node_type == 'sms':
            sms = SMS.objects.get(id=ref_id)
            sms.send(self.user)

            log_event.send(
                self,
                domain='session',
                actor=self.user,
                variable='sms',
                pre_value='',
                post_value=sms.title
            )

            if 'reply:' not in sms.data[0].get('content'):
                self.transition(node_id)

        if node_type == 'register':
            self.user, registered = self.user.register()

            if registered:
                log_event.send(
                    self,
                    domain='user',
                    actor=self.user,
                    variable='registered',
                    pre_value='',
                    post_value=''
                )

            self.transition(node_id)

        if node_type == 'enroll':
            self.session.program.enroll(self.user)

            log_event.send(
                self,
                domain='program',
                actor=self.user,
                variable='enrolled',
                pre_value='',
                post_value=self.session.program.title
            )

            self.transition(node_id)

        if node_type == 'leave':
            self.session.program.leave(self.user)

            log_event.send(
                self,
                domain='program',
                actor=self.user,
                variable='left',
                pre_value='',
                post_value=self.session.program.title
            )

            self.transition(node_id)

        if node_type == 'delay':
            useraccesses = self.session.program.programuseraccess_set.filter(user=self.user)
            for useraccess in useraccesses:
                start_time = self.session.get_start_time(
                    useraccess.start_time,
                    useraccess.time_factor
                )
                delay = node.get('delay')
                kwargs = {
                    delay.get('unit'): float(delay.get('number') * useraccess.time_factor),
                }
                delta = timedelta(**kwargs)

                from system.tasks import transition

                Task.objects.create_task(
                    sender=self.session,
                    domain='delay',
                    time=start_time + delta,
                    task=transition,
                    args=(self.session.id, node_id, self.user.id),
                    action=_('Delayed node execution'),
                    subject=self.user
                )

    def run(self, next=False, pop=False):
        '''
        Run the Engine after initializing and return a node if available

        If next=True, immediately transitions to the next node in current
        session.

        If pop=True, session and node is popped from the users stack and
        initialized.
        '''

        node_id = self.user.data.get('node')

        if node_id is None:
            self.user.data['node'] = 0
            self.user.save()

        # transition to next page
        if next:
            return self.transition(node_id)

        # pop stack data and set previous session
        if pop:
            session_id, node_id = self.user.data.get('stack').pop()
            # pop again if still on the same session
            # risky, but ensures restacking via e.g. menu will not lock user in
            while self.user.data.get('stack') and session_id == self.user.data.get('session'):
                session_id, node_id = self.user.data.get('stack').pop()

            self.init_session(session_id, node_id)

            return self.transition(node_id)

        return self.trigger_node(node_id)
