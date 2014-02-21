
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

