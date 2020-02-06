# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from builtins import object
from datetime import timedelta, datetime
import pytz
import re

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from events.signals import log_event
from system.models import Variable, Session, Page, Email, SMS
from tasker.models import Task
from .expressions import Parser

import logging


class EngineException(Exception):
    pass


class Engine(object):
    '''A simplified decision engine to traverse the Session graph for a user'''

    def __init__(self, user=None, user_id=None, context={}, push=False, is_interactive=False):
        '''
        Initialize Engine with a User or user id and optional context.

        The argument user accepts a user instance, which gives support for
        unconventional user models (e.g. users.StatefulAnonymousUser) or when
        user is known.

        User id should be used for tasks, which should not have complex types.

        If argument push is True, current session and node will be pushed to
        a stack, so the user may return there.
        '''

        self.logger = logging.getLogger('debug')
        self.now = timezone.now()
        self.is_interactive = is_interactive

        if user:
            self.user = user
        else:
            self.user = get_user_model().objects.get(id=user_id)

        self.logger.debug(
            '%s engine init, context %s',
            user, context
        )

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

            for key, value in list(context.items()):
                if key in ('session', 'node'):
                    continue

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

        self.init_session(
            session_id=context.get('session'),
            node_id=context.get('node'),
            should_save=is_interactive
        )

    def init_session(self, session_id=None, node_id=None, should_save=True):

        session_id = session_id or self.user.data.get('session')
        if node_id is None:
            node_id = self.user.data.get('node')

        if should_save:
            self.user.data['session'] = session_id
            self.user.data['node'] = node_id
            self.user.save()

        self.session = Session.objects.get(id=session_id)

        self.nodes = {node['id']: node for node in self.session.data.get('nodes')}
        self.edges = self.session.data.get('edges')
        self.node_id = node_id

        self.logger.debug(
            '%s %s session initialized, node_id %s',
            self.user, self.session, node_id
        )

    def get_node_edges(self, source_id):
        '''Get the edges going from a given node'''
        return [edge for edge in self.edges if edge.get('source') == source_id]

    def get_normal_edges(self, edges):
        '''Get the edges marked normal (foreground) in a list of edges'''
        return [edge for edge in edges if edge.get('type') == 'normal']

    def get_special_edges(self, edges):
        '''Get the edges marked special (background) in a list of edges'''
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
        '''Transition from a given node and trigger a new node.'''

        self.logger.debug(
            '%s %s triggered transition, source_id %s',
            self.user, self.session, source_id
        )

        # keep a local list of nodes
        # self.nodes may have changed when the call stack returns here
        nodes = self.nodes
        edges = self.get_node_edges(source_id)
        special_edges = self.get_special_edges(edges)
        normal_edges = self.get_normal_edges(edges)

        result = None

        # traverse all special edges
        while special_edges:
            edge = self.traverse(special_edges, source_id)

            if edge:
                special_edges.remove(edge)
                target_id = edge.get('target')
                node = nodes.get(target_id)
                result = self.trigger_node(node) or result
            else:
                break

        self.logger.debug(
            '%s %s transition processed special edges, source_id %s',
            self.user, self.session, source_id
        )

        # sometimes a special edge will return a normal node
        # if so, return it
        if result:
            return result

        # traverse first applicable normal edge
        edge = self.traverse(normal_edges, source_id)

        if edge:
            target_id = edge.get('target')
            node = nodes.get(target_id)
            self.logger.debug(
                '%s %s transition returned node %s, edge %s, source_id %s',
                self.user, self.session, node, edge, source_id
            )
            return self.trigger_node(node)
        else:
            self.logger.debug(
                '%s %s transition met dead end, edge %s, source_id %s',
                self.user, self.session, edge, source_id
            )
            return self.handle_dead_end(source_id)

    def trigger_node(self, node):
        '''Trigger action for a given node, return if normal node'''

        node_id = node.get('id')
        node_type = node.get('type')
        ref_id = node.get('ref_id')

        # guard against occational missing ref_id due to error in plumbing
        if not ref_id:
            try:
                ref_id = re.findall(r'\d+', node.get('ref_url', ''))[0]
            except IndexError:
                pass

        self.logger.debug(
            '%s %s triggered node %s, type %s',
            self.user, self.session, node_id, node_type,
        )

        if node_type == 'start':

            return self.transition(node_id)

        if node_type == 'page':

            page = Page.objects.get(id=ref_id)
            page.update_html(self.user)

            page.dead_end = self.is_dead_end(node_id)
            page.stacked = self.is_stacked()
            page.is_chapter = page.chapter is not None
            page.chapters = page.render_section(self.user)
            page.read_only = False
            page.is_back = page.chapter and page.chapter.get_previous() is not None

            if 'node' in self.user.data and self.user.data['node'] in self.nodes:
                # TODO: Better fix
                log_event.send(
                    self,
                    domain='session',
                    actor=self.user,
                    variable='transition',
                    pre_value=self.nodes[self.user.data['node']]['title'],
                    post_value=page.title
                )

            self.user.data['session'] = self.session.id
            self.user.data['node'] = node_id
            if self.user.is_authenticated:
                self.user.register_chapter_to_page(page)
            self.user.save()

            return page

        if node_type == 'wait':

            if self.is_interactive:
                return self.transition(node_id)

            self.user.data['session'] = self.session.id
            self.user.data['node'] = node_id
            self.user.save()

            log_event.send(
                self,
                domain='session',
                actor=self.user,
                variable='wait',
                pre_value='Start Wait',
                post_value=''
            )

            return

        if node_type == 'session':

            if len(self.get_node_edges(node_id)):
                stack = self.user.data.get('stack', [])
                stack.append((self.session.id, node_id))
                self.user.data['stack'] = stack
                self.user.save()

            self.init_session(ref_id, 0)

            return self.transition(0)

        if node_type == 'background_session':

            current_node = node_id
            current_session = self.session.pk
            is_interactive = self.is_interactive
            self.is_interactive = False

            # XXX: Create a new instance of engine?
            self.init_session(ref_id, 0, should_save=False)

            self.transition(0)
            self.is_interactive = is_interactive
            self.init_session(current_session, current_node, should_save=False)

            return self.transition(node_id)

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

            self.logger.debug(
                '%s %s processed expression %s',
                self.user, self.session, expression
            )

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

            self.logger.debug(
                '%s %s email sent %s',
                self.user, self.session, email
            )

            return self.transition(node_id)

        if node_type == 'sms':

            sms = SMS.objects.get(id=ref_id)
            if self.is_interactive and 'reply:' in sms.data[0].get('content'):
                return

            sms.send(self.user, session_id=self.session.id, node_id=node_id)

            log_event.send(
                self,
                domain='session',
                actor=self.user,
                variable='sms',
                pre_value='',
                post_value=sms.title
            )

            self.logger.debug(
                '%s %s sms sent %s',
                self.user, self.session, sms
            )

            if 'reply:' not in sms.data[0].get('content'):
                return self.transition(node_id)
            else:
                return Page()

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

            self.logger.debug(
                '%s %s registered %s',
                self.user, self.session, registered
            )

            return self.transition(node_id)

        if node_type == 'enroll':

            start_time_string = node.get('start_time')
            start_time = timezone.localtime(timezone.now())
            if start_time_string:
                try:
                    hour, minute = start_time_string.split(':')
                    start_time = start_time.replace(
                        hour=int(hour),
                        minute=int(minute),
                        second=0,
                        microsecond=0
                    )
                except:
                    pass

            self.session.program.enroll(self.user, start_time=start_time)

            log_event.send(
                self,
                domain='program',
                actor=self.user,
                variable='enrolled',
                pre_value='',
                post_value=self.session.program.title
            )

            self.logger.debug(
                '%s %s enrolled in %s',
                self.user, self.session, self.session.program
            )

            return self.transition(node_id)

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

            self.logger.debug(
                '%s %s left %s',
                self.user, self.session, self.session.program
            )

            return self.transition(node_id)

        if node_type == 'delay':
            useraccesses = self.session.program.programuseraccess_set.filter(user=self.user)
            for useraccess in useraccesses:

                start_time = datetime.now(pytz.utc)
                delay = node.get('delay')
                variable_name = delay.get('variable')
                delay_number = delay.get('number')
                if variable_name:
                    try:
                        # if variable is dynamically changed in the graph tree (back office)
                        if variable_name in self.user.data :
                            delay_number = int(self.user.data.get(variable_name))
                            self.logger.debug("Delay node using variable: %s => %s" % (variable_name, delay_number))
                        else :
                        # trying to get the predefined value of the variable from the database
                            delay_number = int(Variable.objects.get(name=variable_name).get_value())
                            self.logger.debug("Delay node using variable: %s => %s" % (variable_name, delay_number))
                    except Exception as e:
                        self.logger.error("failed to use variable(%s) in delay node: %s" % (variable_name, e.message))
                else:
                    self.logger.debug("Delay node not using a variable")

                kwargs = {
                    delay.get('unit'): float(delay_number * useraccess.time_factor),
                }
                delta = timedelta(**kwargs)


                from system.tasks import transition

                task = Task.objects.create_task(
                    sender=self.session,
                    domain='delay',
                    time=start_time + delta,
                    task=transition,
                    args=(
                        self.session.id,
                        node_id,
                        self.user.id,
                        self.user.data.get('stack', [])
                    ),
                    action=_('Delayed node execution'),
                    subject=self.user
                )

                self.logger.debug(
                    '%s %s delay created task %s',
                    self.user, self.session, task
                )

                return

    def show_chapter(self, chapter_id):
        # todo: fill the page in case it's a form
        page_id = self.user.get_page_id_by_chapter(chapter_id)
        if page_id:
            page = Page.objects.get(id=page_id)
            page.update_html(self.user)

            next_chapter = page.chapter.get_next()
            page.dead_end = not (next_chapter and self.user.get_page_id_by_chapter(next_chapter.id))
            page.stacked = False
            page.read_only = True
            page.is_chapter = page.chapter is not None
            page.chapters = page.render_section(self.user)
            page.is_back = page.chapter and page.chapter.get_previous() is not None

            if 'node' in self.user.data and self.user.data['node'] in self.nodes:
                log_event.send(
                    self,
                    domain='session',
                    actor=self.user,
                    variable='show_chapter',
                    pre_value=self.nodes[self.user.data['node']]['title'],
                    post_value=page.title
                )

            return page


    def run(self, next=False, pop=False, chapter=0, back=0):
        '''
        Run the Engine after initializing and return a node if available

        If next=True, immediately transitions to the next node in current
        session.

        If pop=True, session and node is popped from the users stack and
        initialized.

        If chapter>0, for view purpose, get the page related to the chapter (id)
        if exists.

        If nav != 0, for view purpose, get the next page (positive id) /
        previous page (negative id) in module by current page_id (id) if exists.
        '''

        self.logger.debug(
            '%s %s run, next %s, pop %s, chapter %s',
            self.user, self.session, next, pop, chapter
        )

        node_id = self.node_id if self.node_id is not None else self.user.data.get('node')

        if node_id is None:
            self.user.data['node'] = 0
            self.user.save()

        if back:
            '''
            Return back page by the current page id (view)
            '''
            page = Page.objects.get(id=back if int(back) > 0 else -int(back))
            if page.chapter:
                nav_to_chapter = page.chapter.get_next() if int(back) > 0 else page.chapter.get_previous()
                if nav_to_chapter:
                    page = self.show_chapter(nav_to_chapter.id)
                    if page:
                        node = self.nodes.get(node_id)
                        current_page = self.trigger_node(node)
                        if page.id == current_page.id:
                            return current_page
                        return page

        if chapter:
            '''
            Return only the page related to the chapter
            '''
            page = self.show_chapter(chapter)
            if page:
                node = self.nodes.get(node_id)
                current_page = self.trigger_node(node)
                if page.id == current_page.id:
                    return current_page
                return page

        # transition to next page
        if next:
            return self.transition(node_id)

        # pop stack data and set previous session
        if pop:
            session_id, node_id = self.user.data.get('stack').pop()

            self.logger.debug(
                '%s %s popped session %s, node %s from stack',
                self.user, self.session, session_id, node_id
            )

            # pop again if still on the same session
            # risky, but ensures restacking via e.g. menu will not lock user in
            while self.user.data.get('stack') and session_id == self.user.data.get('session'):
                session_id, node_id = self.user.data.get('stack').pop()

                self.logger.debug(
                    '%s %s popped session %s, node %s from stack',
                    self.user, self.session, session_id, node_id
                )

            self.init_session(session_id, node_id)

            node = self.nodes.get(node_id)
            if node.get('type') not in ('session', 'background_session'):
                return self.trigger_node(node)

            return self.transition(node_id)

        node = self.nodes.get(node_id)
        return self.trigger_node(node)
