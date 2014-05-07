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

    def traverse(self, source_id):
        '''Select first edge where the user passes edge conditions, return its id'''

        edges = [edge for edge in self.edges if edge.get('source') == source_id]

        for edge in edges:
            conditions = edge.get('conditions')
            target_id = edge.get('target')

            if not conditions:
                return target_id

            else:
                for condition in conditions:

                    key = condition.get('var_name')
                    op = condition.get('operator')
                    val = condition.get('value')

                    user_val = self.user.data.get(key)

                    if user_val:

                        if op == 'eq':
                            if user_val == val:
                                return target_id

                        if op == 'ne':
                            if user_val != val:
                                return target_id

                        if op == 'lt':
                            if user_val < val:
                                return target_id

                        if op == 'le':
                            if user_val <= val:
                                return target_id

                        if op == 'gt':
                            if user_val > val:
                                return target_id

                        if op == 'ge':
                            if user_val >= val:
                                return target_id

                        if op == 'in':
                            if user_val in val:
                                return target_id

    def transition(self, source_id):
        '''Transition from a given node and trigger a new node'''

        target_id = self.traverse(source_id)

        self.user.data['current_node'] = target_id
        self.user.save()

        return trigger_node(target_id)

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

            Task.objects.create_task(
                sender=self.part,
                time=self.part.start_time + delta,
                task=transition,
                args=(user),
                action=_('Delayed node execution')
            )

            return

        if node_type == 'email':

            email = Email.objects.get(id=ref_id)
            email.send(self.user)

            return trigger_node(self.traverse(node_id))

        if node_type == 'sms':

            sms = SMS.objects.get(id=ref_id)
            sms.send(self.user)

            return trigger_node(self.traverse(node_id))

        if node_type == 'start':
            return self.transition(node_id)

    def run(self):
        '''Run the Engine after initializing and return some result'''

        node_id = self.user.data.get('current_node')
        return self.trigger_node(node_id)

