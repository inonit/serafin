
class Context:

    PERMANENT = 1
    SESSION   = 2
    MESSAGE   = 3

    def __init__(self, permanent, session, message):
        self.permanent = permanent
        self.session = session
        self.message = message

    def all(self):
        return dict(self.permanent.items(), self.session.items(), self.message.items())

    def __getitem__(self, key):
        if key in self.message:
            return self.message[key]
        if key in self.session:
            return self.session[key]
        if key in self.permanent:
            return self.permanent[key]
        raise KeyError("key %s not in context" % key)

    def set(self, key, value, scope):
        if scope == self.MESSAGE:
            self.message[key] = value
        elif scope == self.SESSION:
            self.session[key] = value
        elif scope == self.PERMANENT:
            self.permanent[key] = value
        else:
            raise KeyError("invalid scope %s" % scope)


class Scheduler:

    def __init__(self, system):
        self.system = system

    def scheduleNow(self, program_name):
        pass

    def scheduleAt(self, program_name, time)
        pass

    def runScheduledJobs(self, program_name):
        self.system.runScheduledJobs(program_name)


#HumanInteface is *the* object which sits between the system (the Django-app) and the human
#There is no communication outside of it
#Both parties, Django-app on the one hand and system on the other communicate with the Human Interface from each side in order to
#communicate with each other

class HumanInterface:

    def send(self, stimuli):
        pass

    def getResponses()

    def _interpretWebRequest(self, request):
        pass

    def _interpretSMS(self, sms):
        pass

    def _interpretEmail(self, email):
        pass


class Example:

    def web_usage(self):
        human_interface = HumanInterface()
        system = System(human_interface)

        human_responses = human_interface.getResponses()
        
        system.processResponses(human_responses)


class System:

    def __init__(self, human_interface):
        self.scheduler = Scheduler(self)
        self.programs = self.readPrograms()
        self.context = self.readContext()
        self.human_interface = human_interface

    def readPrograms(self):
        pass

    def readContext(self):
        pass

    def programByName(self, name):
        return self.programs[name]

    def processResponses(self, responses):
        all_stimuli = []
        for program_name in self.context["programs"]
            program = self.programByName(program_name)
            stimuli = program.execute(self.context["programContext"], responses)
            all_stimuli = all_stimuli + stimuli
        return all_stimuli

    def runScheduledJobs(self, program_name):
        program = self.programByName(program_name)
        stimuli = program.runScheduledJobs(self.context)
        return stimuli


class SerafSystem(System):

    def runScheduledJobs(self, program_name):
        stimuli = super(SerafSystem, self).runScheduledJobs(program_name)
        



class Program:

    def __init__(self, system):
        self.system = system

    def name(self):
        pass

    def execute(self, context, data):
        pass

    def runScheduledJobs(self, context):
        pass


class State:

    def __init__(self, name):
        self.name = name

    def entryAction(self, context, data):
        pass


class NodeState(State):

    def __init__(self):
        self.arcs = []




class Arc:

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def condition(self, context, data):
        return True


class AbstractStateMachine(model.Model, Program):

    def __init__(self, system, initial_state, states):
        super(AbstractStateMachine, self).__init__(system)
        self.initial_state = initial_state
        self.states = states

    def execute(self, context, data):
        return self.transition(context, data)

    def current_state(self, context):
        try:
            return self.states[context["programs"][self.name]["state"]]
        except:
            return self.initial_state

    def transition(self, context, data):
        state = self.current_state
        for a in state.arcs:
            if a.condition(context, data):
                return self.enterState(a.tail, context)

    def enterState(self, state, context, data):
        program_context = context["programs"][self.name]
        program_context["old_state"] = self.current_state.name
        program_context["state"] = state.name

        return state.entryAction(context, data)

    def runScheduledJobs(self, context):
        pass

