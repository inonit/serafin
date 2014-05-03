from collections import deque
import datetime
from system import SystemVariable
from users.models import UserManager
from django.http import HttpRequest


class RecursiveDict:
    '''
    A recursive dict
    '''
    def __init__(self, items=dict()):
        self.items = items

    def __getitem__(self, key):
        '''Get an item'''
        keys = key.split('.')
        item = self.items
        for k in keys:
            item = item[k]
        return item

    def __setitem__(self, key, value):
        '''Set an item'''
        keys = key.split('.')
        item = self.items
        for k in keys[:-1]:
            if k not in item:
                item[k] = dict()
            item = item[k]
        item[keys[-1]] = value

    def __delitem__(self, key):
        '''Delete an item'''
        keys = key.split('.')
        item = self.items
        for k in keys[:-1]:
            item = item[k]
        del item[keys[-1]]

    def __iter__(self):
        '''Iterate'''
        stack = [(None, self.items)]
        while stack:
            index, item = stack.pop()
            if type(item) is dict:
                for i in reversed(item.keys()):
                    stack.append((index+'.'+i if index else i, item[i]))
                continue
            yield index

    def keys(self):
        return list(self.__iter__())


class Scope(RecursiveDict):
    def persist(self):
        raise NotImplemented

    @staticmethod
    def fromRequest(request):
        request_interpreter = RequestInterpreter()
        return MessageScope(request, request_interpreter.interpret(request))

    @staticmethod
    def fromMessage(message):
        if isinstance(message, HttpRequest):
            return self.fromRequest(message)
        if isinstance(message, SmsMessage):
            return self.fromSms(message)
        if isinstance(message, EmailMessage):
            return self.fromEmail(message)

    @staticmethod
    def fromEmail(email):
        raise NotImplemented

    @staticmethod
    def fromSms(sms):
        raise NotImplemented

    @staticmethod
    def fromSession(session):
        variables = dict()
        for key, value in session:
            variables[key] = value
        return SessionScope(session, variables)

    @staticmethod
    def fromUser(user):
        variables = dict()
        for key, value in user.data:
            variables[key] = value
        return UserScope(user, variables)

    @staticmethod
    def fromSystem(manager):
        variables = dict()
        for var in manager.all():
            variables[var.key] = var.value
        return SystemScope(manager, variables)


class MessageScope(Scope):
    def persist(self):
        pass  # no need to persist the message scope


class SessionScope(Scope):
    def __init__(self, session, items=dict()):
        Scope.__init__(self, items)
        self.session = session

    def persist(self):
        to_set = []
        to_delete = []

        for key in self.session:

            if key in self.items:
                if self.session[key] != self.items[key]:
                    to_set.append((key, self.items[key]))
            else:
                to_delete.append(key)

        for key in self.items:
            if key not in self.session:
                to_set.append((key, self.items[key]))

        for key in to_delete:
            del self.session[key]

        for key, value in to_set:
            self.session[key] = value


class UserScope(Scope):
    def __init__(self, user, items=dict()):
        Scope.__init__(self, items)
        self.user = user

    def persist(self):
        self.user.data = self.items
        self.user.save()


class SystemScope(Scope):
    def __init__(self, manager, items=dict()):
        Scope.__init__(self, items)
        self.manager = manager

    def persist(self):
        to_add = []
        to_change = []
        to_delete = []
        persisted_vars = self.manager.all()
        persisted_vars_dict = dict()
        for var in persisted_vars:
            persisted_vars_dict[var.key] = var

            if var.key in self.items:
                if var.value != self.items[var.key]:
                    to_change.append((var.key, self.items[var.key]))
            else:
                to_delete.append(var.key)

        for key in self.items:
            if key not in persisted_vars_dict:
                to_add.append((key, self.items[key]))

        for key in to_delete:
            self.manager.delete(key)

        for key, value in to_add:
            self.manager.create(key=key, value=value)

        for key, value in to_change:
            var = persisted_vars_dict[key].value
            var.value = value
            var.save()


class ScopeStack:
    def __init__(self):
        self.scopes = deque()

    def add_scope(self, scope):
        self.scopes.appendleft(scope)

    def __getitem__(self, key):
        '''Get an item'''
        for scope in self.scopes:
            if key in scope:
                return scope[key]
        raise KeyError('key %s is undefined' % key)

    def __setitem__(self, key, value):
        '''Set an item'''
        for scope in self.scopes:
            if key in scope:
                scope[key] = value
        raise KeyError('key %s is undefined' % key)  # TODO: setting new keys

    def __delitem__(self, key, value):
        '''Delete an item'''
        for scope in self.scopes:
            if key in scope:
                del scope[key]
        raise KeyError('key %s is undefined' % key)


class Context(ScopeStack):
    def persist(self):
        for scope in self.scopes:
            scope.persist()

    @staticmethod
    def fromRequest(request):
        return Context.fromScopes([
            Scope.fromSystem(SystemVariable.objects),
            Scope.fromUser(request.user),
            Scope.fromSession(request.session),
            Scope.fromRequest(request)])

    @staticmethod
    def fromMessage(message):
        if isinstance(message, HttpRequest):
            return self.fromRequest(message)

        return Context.fromScopes([
            Scope.fromSystem(SystemVariable.objects),
            Scope.fromUser(message.user),
            Scope.fromMessage(message)])

    @staticmethod
    def fromEmail(email):
        raise NotImplemented

    @staticmethod
    def fromSms(sms):
        raise NotImplemented

    @staticmethod
    def fromUser(user):
        return Context.fromScopes([
            Scope.fromSystem(SystemVariable.objects),
            Scope.fromUser(user)])

    @staticmethod
    def fromUserId(user_id):
        return Context.fromUser(UserManager.get(user_id))

    @staticmethod
    def fromScopes(scopes):
        context = Context()
        for scope in scopes:
            context.add_scope(scope)
        return context


class System:
    '''
    A system is a collection of programs and a scheduler
    '''
    def __init__(self, scheduler, context):
        self.programs = dict()
        self.scheduler = scheduler
        self.context = context

    def run(self):
        '''Execute all running programs'''
        responses = []

        running_programs = self.get_running_programs()
        if running_programs == []:
            raise KeyError("No running programs")

        for program in running_programs:
            responses.append(program.run(self.context))
        return responses

    def run_job(self, job_id):
        '''Run a job of a particular program'''
        return program.run_job(job_id, self.context)

    def get_program_by_name(self, name):
        '''Get program by its name'''
        return self.programs[name]

    def get_running_programs(self):
        '''Get the programs that are running'''
        return [program for program in self.programs
                if self.context['system.programs.'+program.name+'.is_running']]


class Program:
    '''
    A program is a named entity that can be run

    Programs also define a collection of jobs that can be run
    '''
    def __init__(self, name):
        self.name = name

    def run(self):
        '''Run the program'''
        raise NotImplemented

    def run_job(self, job_name):
        '''Run a program job'''
        raise NotImplemented


class Scheduler:
    '''
    A scheduler is an entity that can schedule execution of
    program jobs.

    Execution of program jobs can be scheduled to happen right away
    or on/at a certain date/time.
    '''
    def add_job(self, job_id, date=None):
        '''Get the job execution time by job id'''
        raise NotImplemented

    def reschedule_job(self, job_id, date=None):
        '''Set the job execution time by job id'''
        raise NotImplemented

    def delete_job(self, job_id):
        '''Delete a job by job id'''
        raise NotImplemented

    def run_job(self, args):
        '''Run a job'''

        context = Context.fromUserId(args['user_id'])
        system = System(programs, self, context)


class Node:
    '''
    A node is a named entity that is connected to other nodes through arcs.

    A node's arcs are split into incoming and outgoing.
    '''
    def __init__(self, name):
        self.name = name
        self.incoming = []
        self.outgoing = []


class State(Node):
    '''
    A state is a node that can be entered.

    A state has an entry action.

    A state is final if it has no outgoing arcs.
    '''
    def entry_action(self, context, message_interface):
        '''Fires the entry action of the state'''
        raise NotImplemented

    def is_final(self):
        '''A state is final if it has no outgoing arcs.'''
        return not self.outgoing


class ResponseState(State):
    '''
    A response state is a state whose entry_action produces a response.
    '''
    pass


class ReentrantState(State):
    '''
    A reentrant state is a state which can be re-entered without side effects.
    '''
    pass


class HttpState(ResponseState, ReentrantState):
    '''
    An HTTP state is a re-entrant response state whose response is sent using
    HTTP.
    '''
    pass


class SmsState(ResponseState):
    '''
    An SMS state is a response state whose response is sent using SMS.
    '''
    pass


class EmailState(ResponseState):
    '''
    An e-mail state is a response state whose response is sent using e-mail.
    '''
    pass


class ActionState(State):
    '''
    An action state is a state that should be left as soon as it's entry action
    has been run.
    '''
    pass


class PersistentState(State):
    '''
    A persistent state is a state you can stay in.
    '''
    pass



class DelayState(State):
    pass


class AbsoluteDelayState(State):
    '''
    A delay state is a state that should be left after a given delay.
    '''
    def __init__(self, name, delay_date=datetime.datetime.now()):
        Node.__init__(self, name)
        self.set_delay_date(delay_date)

    def set_delay_duration(self, seconds):
        delay_date = datetime.datetime.now() + datetime.timedelta(seconds=15)
        self.set_delay_date(delay_date)

    def set_delay_date(self, date):
        self.delay_date = date

    def get_delay_date(self):
        return self.delay_date


class RelativeDelayState(State):
    '''
    A delay state is a state that should be left after a given delay.
    '''
    def __init__(self, name, delay_duration=0):
        Node.__init__(self, name)
        self.set_delay_date(delay_date)

    def set_delay_duration(self, seconds):
        delay_date = datetime.datetime.now() + datetime.timedelta(seconds=15)
        self.set_delay_date(delay_date)

    def set_delay_date(self, date):
        self.delay_date = date

    def get_delay_date(self):
        return self.delay_date



class Arc:
    '''
    An arc is a pair of nodes.
    '''
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def persist(self):
        '''Persist the arc to its nodes'''
        self.head.outgoing.append(self)
        self.tail.incoming.append(self)


class Transition(Arc):
    '''
    A transition is an arc that has a condition.
    '''
    def condition(self, context, data):
        '''Can this arc be followed?'''
        return True

    def fromState(self):
        return self.head


class TransitionError(Exception):
    '''
    Raised when a state transition that is not allowed is attempted
    '''
    def __init__(self, state, msg=''):
        self.state = state
        self.msg = msg

    def __str__(self):
        return ("transition error in state %s: %s" %
                    (self.state, self.msg))


class UnknownCurrentStateError(TransitionError):
    '''
    Raised when the current state is unknown
    '''
    def __init__(self):
        TransitionError.__init__(self, 'unknown', 'current state is unknown')


class FinalStateError(TransitionError):
    '''
    Raised when a transition from a final state is attempted
    '''
    def __init__(self, state):
        TransitionError.__init__(self, state, 'state is final')


class MessageInterpreter:
    def interpret(object):
        raise NotImplemented


class RequestInterpreter(MessageInterpreter):
    def interpret(request):
        message_variables = dict()
        for key, value in request.POST['variables']:
            message_variables[key] = value
        return dict({'message': message_variables})


class EmailInterpreter(MessageInterpreter):
    pass


class SmsInterpreter(MessageInterpreter):
    pass


class MessageInterface:
    def send(self, message):
        raise NotImplemented

    def receive(self):
        raise NotImplemented


class BufferingMessageInterface:
    def __init__(self):
        self.sent = []
        self.received = []

    def send(self, message):
        self.sent.append(message)

    def receive(self):
        yield self.received.pop()

    def add_receied(self, message):
        self.received.append(message)

    def get_sent(self):
        return self.sent


class Message:
    pass


class EmailMessage(Message):
    pass


class SmsMessage(Message):
    pass


class AbstractStateMachine(Program):
    '''
    An abstract state machine is a program that is represented by a finite
    state machine with abstract transition conditions and state entry actions.

    An abstract state machine is defined by:
     - a collection of states
     - the initial state
    '''
    def __init__(self, name, states, initial_state):
        Program.__init__(self, name)
        self.states = states
        self.initial_state = initial_state

    def run(self, context, message_interface):
        '''Overriding Program's run method'''
        current_state = self.get_current_state(context)
        if current_state is None:
            raise UnknownCurrentStateError

        if self.get_should_transition(context):
            self.make_transition(current_state, context, message_interface)
        else:
            current_state.entry_action(context, message_interface)

    def get_should_transition(self, context):
        try:
            return context["make_transition"]
        except:
            return False

    def get_current_state(self, context):
        '''Get the current state'''
        try:
            return self.states[context["system.programs." + self.name +
                                       ".current_state"]]
        except:
            return None

    def set_current_state(self, state, context):
        '''Set the current state'''
        context["system.programs." + self.name + ".current_state"] = state.name

    def make_transition(self, from_state, context, message_interface):
        '''Make a machine transition'''

        # use deque to enforce depth-first traversal
        state_queue = deque()
        visited_passthrough_states = dict()
        for transition in from_state.outgoing:
            if transition.condition(context):
                state_queue.append(transition.tail)

        if not state_queue:
            pass  # TODO: kill program

        while state_queue:
            state = state_queue.popleft()

            if isinstance(state, ActionState) or isinstance(state, DelayState):
                if state.name in visited_passthrough_states:
                    continue  # TODO: log error
                visited_passthrough_states[state.name] = True

            if isinstance(state, ActionState):
                for transition in state.outgoing:
                    if transition.condition(context):
                        state_queue.append(transition.tail)

            if isinstance(state, PersistentState):
                self.change_state(state, context)

            state.entry_action(context, message_interface)

    def change_state(self, new_state, context):
        '''Change the state from current state to new_state'''
        current_state = self.get_current_state(context)
        self.set_previous_state(current_state, context)
        self.set_current_state(new_state, context)

    def run_job(self, job_name, context):
        '''Run a job'''
        if job_name == 'depart_expired_state':
            self.depart_expired_state(context)

    def depart_expired_state(self, context):
        '''Depart expired state'''
        current_state = self.get_current_state(context)

        if current_state is None:
            raise UnknownCurrentStateError
        else:
            if current_state.has_expired():
                for transition in current_state.on_expiration:
                    if transition.condition(context):
                        return self.change_state(current_state,
                                                 transition.tail,
                                                 context)


class SerafProgram(AbstractStateMachine):
    def fromPart(part):
        states = []
        for node in part.data['nodes']:
            if 'type' in node:
                if node['type'] == 'delay':
                    state = DelayState()
        seraf_program = SerafProgram(part.program.title+'.'+part.title, states, initial_state)

    def get_variables(self, data):
        variables = []
        stack = deque(data)
        while stack:
            item = stack.popleft()
            if 'content_type' in item and item['content_type'] == 'form':
                stack.extentleft(item['content'])
            elif 'variable_name' in item:
                variables.append(item)
        return variables

