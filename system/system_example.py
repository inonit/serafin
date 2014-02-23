from system import *

import time

class TextAwareState(State):

    def __init__(self, name, text):
        State.__init__(self, name)
        self.text = text

    def has_expired(self, context):
        return False


class Page(TextAwareState):

    def entry_action(self, context):
        return [ConsoleResponse(self.text)]


class Choice(TextAwareState):

    def __init__(self, name, text, var):
        TextAwareState.__init__(self, name, text)
        self.var = var

    def entry_action(self, context):
        return [ConsoleChoiceResponse(self.text, self.var)]


class Sms(TextAwareState):

    def entry_action(self, context):
        return [ParametrizedSmsResponse(self.text, context['cigarettes'])]


class GreaterThanZeroAnswerArc(Arc):

    def __init__(self, head, tail, var):
        Arc.__init__(self, head, tail)
        self.var = var

    def condition(self, context):
        return int(context[self.var]) > 0


class LessThanOrEqualZeroAnswerArc(Arc):

    def __init__(self, head, tail, var):
        Arc.__init__(self, head, tail)
        self.var = var

    def condition(self, context):
        return int(context[self.var]) <= 0


class PassArc(Arc):

    def condition(self, context):
        return True


class Response:

    def __init__(self, text):
        self.text = text

    def send(self):
        raise NotImplemented


class SmsResponse(Response):

    def send(self):
        print "SMS:\n" + self.text


class ParametrizedSmsResponse(SmsResponse):

    def __init__(self, text, parameter):
        Response.__init__(self, text)
        self.parameter = parameter

    def send(self):
        print "SMS:\n" + self.text % self.parameter


class ConsoleResponse(Response):

    def send(self):
        print self.text


class ConsoleChoiceResponse(Response):

    def __init__(self, text, name):
        Response.__init__(self, text)
        self.name = name

    def send(self):
        print self.text

    def varname(self):
        return self.name


class Test:

    def run(self):

        start = Page("start", "Start:\nWelcome to this state-of-the-art 'Stop Smoking' program")
        page1 = Page("page1", "Page 1:\nYou need to stop smoking!")
        page2 = Page("page2", "Page 2:\nSeriously!")
        choice = Choice("choice", "Choice:\nHow many cigarettes will you smoke from now on?", "cigarettes")
        sms = Sms("sms", 'Bad! %s is too many! Try 0')
        page3 = Page("page3", "Page 3:\nGood job!!!")
        end = Page("end", "End:\nThe end!")

        PassArc(start, page1)
        PassArc(page1, page2)
        PassArc(page2, choice)
        GreaterThanZeroAnswerArc(choice, sms, "cigarettes")
        LessThanOrEqualZeroAnswerArc(choice, page3, "cigarettes")
        PassArc(sms, end)
        PassArc(page3, end)

        states = dict()
        states["start"] = start
        states["page1"] = page1
        states["page2"] = page2
        states["page3"] = page3
        states["choice"] = choice
        states["sms"] = sms
        states["end"] = end

        program = AbstractStateMachine("StopSmokingProgram", states, start)

        permanent_scope = Scope("permanent")
        permanent_scope["running_programs"] = ["StopSmokingProgram"]
        permanent_scope["current_program_state"] = dict()
        permanent_scope["previous_program_state"] = dict()

        message_scope = Scope("message")

        context = Context()
        context.scopes.append(permanent_scope)
        context.scopes.append(message_scope)

        scheduler = Scheduler()

        system = System()
        system.programs["StopSmokingProgram"] = program
        system.context = context
        system.scheduler = scheduler

        read_user_input = False
        ask_user_for = ''
        while True:

            if read_user_input:
                read_user_input = False

                value = raw_input()
                message_scope[ask_user_for] = value

            try:
                responses = system.run()
            except FinalStateError:
                return

            for response in responses:
                response.send()
                if isinstance(response, ConsoleChoiceResponse):

                    read_user_input = True
                    ask_user_for = response.varname()

            print

            time.sleep(0.5)


test = Test()
test.run()
