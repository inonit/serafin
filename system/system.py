import pprint
import time

class Scope(dict):

    def __init__(self, name):
        self.name = name


# Context is a stack of scopes
#     GLOBAL
#     PERMANENT
#     SESSION
#     MESSAGE
#     TRANSIENT
class Context:

    def __init__(self):
        self.scopes = []

    def flatten(self):
        flattened = dict()
        for scope in self.scopes:
            for (key, value) in scope.items():
                flattened[key] = value
        return flattened

    def __getitem__(self, key):
        for scope in reversed(self.scopes):
            if key in scope:
                return scope[key]
        raise KeyError("key %s not in context" % key)

    def __setitem__(self, key, value):
        for scope in reversed(self.scopes):
            if key in scope:
                scope[key] = value
        raise KeyError("key %s not in context" % key)


class System:

    def __init__(self):
        self.programs = dict()

    def run(self):
        responses = []

        running_programs = self.get_running_programs()
        if running_programs == []:
            raise KeyError("No running programs")

        for program in running_programs:
            responses += program.run(self.context)
        return responses

    def run_jobs(self, program_name):
        program = self.get_program_by_name(program_name)
        return program.run_jobs(self.context)

    def get_program_by_name(self, name):
        return self.programs[name]

    def get_running_programs(self):
        return [self.get_program_by_name(program_name) for program_name in self.context["running_programs"]]


class Program:

    def __init__(self, name):
        self.name = name

    def run(self, context):
        raise NotImplemented

    def run_jobs(self, context):
        raise NotImplemented


class Scheduler:

    def schedule_now(self, program_name):
        raise NotImplemented

    def schedule_at(self, program_name, time):
        raise NotImplemented

    def run_jobs(self, program_name):
        self.system.run_jobs(program_name)


class SerafSystem(System):

    def run_jobs(self, program_name):
        responses = super(SerafSystem, self).run_jobs(program_name)


#HumanInteface is *the* object which sits between the system (the Django-app) and the human
#There is no communication outside of it
#Both parties, Django-app on the one hand and system on the other communicate with the Human Interface from each side in order to
#communicate with each other

class HumanInterface:

    def send(self, stimuli):
        raise NotImplemented

    def get_responses():
        raise NotImplemented

    def _interpret_web_request(self, request):
        raise NotImplemented

    def _interpret_sms(self, sms):
        raise NotImplemented

    def _interpret_email(self, email):
        raise NotImplemented


class Example:

    def web_usage(self):
        human_interface = HumanInterface()
        system = System(human_interface)
        human_responses = human_interface.get_responses()
        system.process(human_responses)


class Node:

    def __init__(self, name):
        self.name = name
        self.incoming = []
        self.outgoing = []
        self.expiration = []

    def entry_action(self, context):
        raise NotImplemented

    def has_expired(self):
        raise NotImplemented


class State(Node):
    pass


class Arc:

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.head.outgoing.append(self)
        self.tail.incoming.append(self)

    def condition(self, context, data):
        return True


class ValidatorArc(Arc):

    def condition(self, context):
        return context["my_var"] == "Test"


class AbstractStateMachine(Program):

    def __init__(self, name, states, initial_state):
        Program.__init__(self, name)
        self.states = states
        self.initial_state = initial_state

    def run(self, context):
        return self.transition(context)

    def get_current_state(self, context):
        try:
            return self.states[context["current_program_state"][self.name]]
        except:
            return None

    def transition(self, context):
        current_state = self.get_current_state(context)

        if current_state == None:
            return self.enter_state(self.initial_state, context)
        else:
            for arc in current_state.outgoing:
                if arc.condition(context):
                    return self.follow_arc(arc, context)

    def follow_arc(self, arc, context):
        new_state = arc.tail
        return self.enter_state(new_state, context)

    def enter_state(self, state, context):
        previous_state = self.get_current_state(context)
        if previous_state != None:
            context["previous_program_state"][self.name] = previous_state.name

        context["current_program_state"][self.name] = state.name

        return state.entry_action(context)

    def run_jobs(self, context):
        raise NotImplemented


class NormalDay(State):

    def entry_action(self, context):
        return [
            "-------------------------",
            "Day %s." % self.name,
            "",
            "-------------------------",
            ""]

    def has_expired(self, context):
        return False


class Response:

    def __init__(self, text):
        self.text = text

    def send(self):
        raise NotImplemented


class Information(Response):

    def send(self):
        print self.text


class Question(Response):

    def send(self):
        return raw_input(self.text)


class Request:

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Test:

    def run(self):

        state1 = HelloWorldState("state1")
        state2 = HelloWorldState("state2")
        arc1 = ValidatorArc(state1, state2)
        states = dict()
        states["state1"] = state1
        states["state2"] = state2

        program1 = AbstractStateMachine("StupidProgram", states, state1)

        permanent_scope = Scope("permanent")
        permanent_scope["page"] = 1
        permanent_scope["my_var"] = "Test"
        permanent_scope["running_programs"] = ["StupidProgram"]
        permanent_scope["current_program_state"] = dict()
        permanent_scope["previous_program_state"] = dict()

        message_scope = Scope("message")
        message_scope["page"] = 2

        context = Context()
        context.scopes.append(permanent_scope)
        context.scopes.append(message_scope)

        scheduler = Scheduler()

        system = System()
        system.programs["StupidProgram"] = program1
        system.context = context
        system.scheduler = scheduler

        message_scope["page"] = 1

        responses = system.run()
        for response in responses:
            print response

        message_scope["page"] = 2

        responses = system.run()
        for response in responses:
            print response

test = Test()
test.run()
