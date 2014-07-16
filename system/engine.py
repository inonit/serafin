from __future__ import unicode_literals
from django.core.signals import request_finished
from django.utils.translation import ugettext_lazy as _

from events.signals import log_event
from system.models import Variable, Session, Page, Email, SMS
from tasker.models import Task
from huey.djhuey import db_task
import datetime


class Engine(object):
    '''A simplified decision engine to traverse the graph for a user'''

    def __init__(self, user, context={}):
        '''Initialize Engine with a User instance and optional context'''

        self.user = user

        # process context if available, save to user data
        if context:
            for key, value in context.items():
                if key and value is not None:
                    self.user.data[key] = value

            self.user.save()

        session_id = self.user.data.get('current_session')
        self.session = Session.objects.get(id=session_id)

        self.nodes = {node['id']: node for node in self.session.data.get('nodes')}
        self.edges = self.session.data.get('edges')

    def get_system_var(var_name):
        try:
            var = Variable.objects.get(name=var_name)
            return var.get_value()
        except:
            return None

    @classmethod
    def check_conditions(cls, conditions, user, return_value):
        '''Return a value for the first passing condition in a list of conditions'''

        for condition in conditions:
            var_name = condition.get('var_name')
            operator = condition.get('operator')
            value_a = condition.get('value')

            # variable comparison:
            # if value_a is actually another var_name, assign users value to it
            value_a = user.data.get(value_a, value_a)
            value_b = user.data.get(var_name)

            if not value_a:
                value_a = cls.get_system_var(var_name)

            if not value_b:
                value_b = cls.get_system_var(var_name)

            try:
                # try converting to float for numeric comparisons
                value_a_float = float(value_a)
                value_b_float = float(value_b)

                # only set to float if both pass conversion
                value_a = value_a_float
                value_b = value_b_float
            except:
                pass

            if var_name == 'group':
                value_b = ', '.join(
                    [group.__unicode__() for group in user.groups.all()]
                )

            if value_b:
                if operator == 'eq':
                    if value_b == value_a:
                        return return_value

                if operator == 'ne':
                    if value_b != value_a:
                        return return_value

                if operator == 'lt':
                    if value_b < value_a:
                        return return_value

                if operator == 'le':
                    if value_b <= value_a:
                        return return_value

                if operator == 'gt':
                    if value_b > value_a:
                        return return_value

                if operator == 'ge':
                    if value_b >= value_a:
                        return return_value

                if operator == 'in':
                    if unicode(value_a).lower() in unicode(value_b).lower():
                        return return_value

    def traverse(self, edges, source_id):
        '''Select and return first edge where the user passes edge conditions'''

        for edge in edges:
            conditions = edge.get('conditions')

            if not conditions:
                return edge
            else:
                return check_conditions(conditions, self.user, edge)


    def get_node_edges(self, source_id):
        return [edge for edge in self.edges if edge.get('source') == source_id]

    def get_normal_edges(self, edges):
        return [edge for edge in edges if edge.get('type') == 'normal']

    def get_special_edges(self, edges):
        return [edge for edge in edges if edge.get('type') == 'special']

    def is_dead_end(self, node_id):
        target_edges = self.get_node_edges(node_id)
        return len(self.get_normal_edges(target_edges)) == 0

    def transition(self, source_id):
        '''Transition from a given node and trigger a new node'''

        edges = self.get_node_edges(source_id)

        # traverse all special edges
        special_edges = self.get_special_edges(edges)
        while special_edges:
            edge = self.traverse(special_edges, source_id)
            if edge:
                special_edges.remove(edge)
                node = self.trigger_node(edge.get('target'))
            else:
                break

        # traverse first applicable normal edge
        normal_edges = self.get_normal_edges(edges)
        edge = self.traverse(normal_edges, source_id)
        if edge:
            target_id = edge.get('target')
            node = self.trigger_node(target_id)

            if isinstance(node, Page):
                log_event.send(self, domain="session", actor=self.user,
                               variable="transition",
                               pre_value=self.nodes[int(self.user.data.get("current_node"))].get("title"),
                               post_value=node)

                self.user.data['current_node'] = target_id
                self.user.save()

                node.dead_end = self.is_dead_end(target_id)

                return node

    def trigger_node(self, node_id):
        '''Trigger action for a given node, return if Page'''

        node = self.nodes.get(node_id)
        node_type = node.get('type')
        ref_id = node.get('ref_id')

        if node_type == 'page':

            page = Page.objects.get(id=ref_id)
            page.update_html(self.user)

            page.dead_end = self.is_dead_end(node_id)

            return page

        if node_type == 'delay':

            delay = node.get('delay')
            kwargs = {
                delay.get('unit'): delay.get('number'),
            }
            delta = datetime.timedelta(**kwargs)

            from system.tasks import transition
            Task.objects.create_task(
                sender=self.session,
                time=self.session.start_time + delta,
                task=transition,
                args=(self.user, node_id),
                action=_('Delayed node execution')
            )

            log_event.send(self, domain="session", actor=self.user,
                           variable="delay",
                           pre_value="",
                           post_value=u"Delay: {number} {unit}, Node id: {node_id}, Session start time: {start_time}".format(
                               unit=delay.get("unit"),
                               number=delay.get("number"),
                               node_id=node_id,
                               start_time=self.session.start_time
                           ))

            return None

        if node_type == 'email':

            email = Email.objects.get(id=ref_id)
            email.send(self.user)

            log_event.send(self, domain="session", actor=self.user,
                           variable="email",
                           pre_value="",
                           post_value=u"ID: {id}".format(id=ref_id))

            return self.transition(node_id)

        if node_type == 'sms':

            sms = SMS.objects.get(id=ref_id)
            sms.send(self.user)

            log_event.send(self, domain="session", actor=self.user,
                           variable="SMS",
                           pre_value="",
                           post_value=u"ID: {id}".format(id=ref_id))

            return self.transition(node_id)

        if node_type == 'start':
            return self.transition(node_id)

    def run(self, next=None):
        '''Run the Engine after initializing and return some result'''

        node_id = int(self.user.data.get('current_node', 0))

        if next:
            return self.transition(node_id)

        return self.trigger_node(node_id)
