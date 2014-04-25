from django.db.models import Manager


class EventManager(Manager):
    '''Manager class for events'''

    def create_event(self, domain, actor, variable, pre_value, post_value):
        '''Creates an event record'''
        event = self.model(
            domain=domain,
            actor=actor,
            variable=variable,
            pre_value=pre_value,
            post_value=post_value,
        )
        event.save()

        return event
