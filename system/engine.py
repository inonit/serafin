from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from system.models import Part, Page, Email, SMS
from tasker.models import Task
from huey.djhuey import db_task
import datetime


RESERVED_NAMES = [
    'current_part',
    'current_node',
    'group'
]


class Engine(object):
    '''A simplified decision engine to traverse the graph for a user'''

    def __init__(self, user, context={}):
        '''Initialize Engine with a User instance and optional context'''

        self.user = user

        # process context if available, save to user data
        if context:
            for key, value in context.items():
                self.user.data[key] = value

            self.user.save()

        part_id = self.user.data.get('current_part')
        self.part = Part.objects.get(id=part_id)

        self.nodes = {node['id']: node for node in self.part.data.get('nodes')}
        self.edges = self.part.data.get('edges')

    def traverse(self, edges, source_id):
        '''Select and return first edge where the user passes edge conditions'''

        for edge in edges:
            conditions = edge.get('conditions')

            if not conditions:
                return edge

            else:
                for condition in conditions:

                    key = condition.get('var_name')
                    op = condition.get('operator')
                    val = condition.get('value')

                    user_val = self.user.data.get(key)

                    if user_val:

                        if op == 'eq':
                            if user_val == val:
                                return edge

                        if op == 'ne':
                            if user_val != val:
                                return edge

                        if op == 'lt':
                            if user_val < val:
                                return edge

                        if op == 'le':
                            if user_val <= val:
                                return edge

                        if op == 'gt':
                            if user_val > val:
                                return edge

                        if op == 'ge':
                            if user_val >= val:
                                return edge

                        if op == 'in':
                            if user_val in val:
                                return edge

    def get_node_edges(self, source_id):
        return [edge for edge in self.edges if edge.get('source') == source_id]

    def get_normal_edges(self, edges):
        return [edge for edge in edges if edge.get('type') == 'normal']

    def get_special_edges(self, edges):
        return [edge for edge in edges if edge.get('type') == 'special']

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
                self.user.data['current_node'] = target_id
                self.user.save()

                # notify frontend of dead end
                target_edges = self.get_node_edges(target_id)
                node.dead_end = len(self.get_normal_edges(target_edges)) == 0

                return node

    def trigger_node(self, node_id):
        '''Trigger action for a given node, return if Page'''

        node = self.nodes.get(node_id)
        node_type = node.get('type')
        ref_id = node.get('ref_id')

        if node_type == 'page':

            page = Page.objects.get(id=ref_id)
            page.update_html(self.user)

            return page

        if node_type == 'delay':

            delay = node.get('delay')
            kwargs = {
                delay.get('unit'): delay.get('number'),
            }
            delta = datetime.timedelta(**kwargs)

            from system.tasks import transition
            Task.objects.create_task(
                sender=self.part,
                time=self.part.start_time + delta,
                task=transition,
                args=(self.user, node_id),
                action=_('Delayed node execution')
            )

            return None

        if node_type == 'email':

            email = Email.objects.get(id=ref_id)
            email.send(self.user)

            return self.transition(node_id)

        if node_type == 'sms':

            sms = SMS.objects.get(id=ref_id)
            sms.send(self.user)

            return self.transition(node_id)

        if node_type == 'start':
            return self.transition(node_id)

    def run(self, next=None):
        '''Run the Engine after initializing and return some result'''

        node_id = self.user.data.get('current_node')

        if next:
            return self.transition(node_id)

        return self.trigger_node(node_id)
