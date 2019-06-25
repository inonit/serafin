from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

import re


def natural_join(listing):
    if len(listing) == 1:
        return listing[0]

    if len(listing) > 1:
        first = ', '.join(listing[:-1])
        last = listing[-1]
        return _('%(first)s and %(last)s') % locals()

    return ''


def remove_comments(text):
    return re.sub(r'\[\[.*?\]\]', '', text)


def variable_replace(user, text):
    user_data = user.data

    markup = re.findall(r'{{.*?}}', text)
    for code in markup:

        variable = code[2:-2].strip()
        value = user_data.get(variable)
        if isinstance(value, list):
            value = natural_join(value)

        if value is None:
            try:
                from system.models import Variable
                value = Variable.objects.get(name=variable).get_value()
            except:
                pass

        if isinstance(value, float):
            value = unicode(value)
            if value.endswith('.0'):
                value = value[:-2]

        text = text.replace(code, unicode(value))

    return text


def live_variable_replace(user, text):
    user_data = user.data

    variables = {}
    markup = re.findall(r'{{.*?}}', text)
    for code in markup:

        variable = code[2:-2].strip()
        value = user_data.get(variable)
        if isinstance(value, list):
            value = natural_join(value)

        if value is None:
            try:
                from system.models import Variable
                value = Variable.objects.get(name=variable).get_value()
            except:
                pass

        variables[variable] = value
        text = text.replace(code, '<span ng-bind-html="variables.%s | stripzerodecimal | breaks"></span>' % unicode(variable))

    return text, variables

# for toggleset, togglesetmulti, multiplechoice, multipleselection
# try to find if the option value (choicevalue) is already checked previously
# by the user (saved in variable variableName)
def is_it_checked(user, variableName,choiceValue):
    user_data = user.data
    variableValue = user_data.get(variableName)

    if variableValue is None:
        try:
            from system.models import Variable
            variableValue = Variable.objects.get(name=variableName).get_value()
        except:
            pass

    if variableValue is None:
        return False

    if not isinstance(variableValue, list):
        variableValue = [variableValue]

    if choiceValue in variableValue:
        return True
    else:
        return False

def process_email_links(user, text):
    '''Replaces login link markup with login link'''

    matches = re.findall(r'(login_link)', text)
    for match in matches:

        link = user.generate_login_link()
        text = text.replace(match, link)

    return text


def generate_pdfs(user, text):
    '''Replaces login link markup with login link'''

    pdfs = []

    matches = re.findall(r'(pdf:(\d+))', text)
    for match in matches:

        full_match = match[0]
        print(full_match)
        page_id = match[1]

        # try:
        from system.models import Page
        pdf = Page.objects.get(id=page_id).generate_pdf(user)
        pdfs.append(pdf)
        # except:
        #     pass

        text = text.replace(full_match, '')

    return text, pdfs


def process_reply_variables(user, text, **kwargs):
    '''Stores the name of the variable to store SMS replies in'''

    matches = re.findall(r'(reply:([\w_.\-+]+))', text)
    for match in matches:
        reply_str = match[0]
        reply_var = match[1]

        user.data['reply_session'] = kwargs.get('session_id')
        user.data['reply_node'] = kwargs.get('node_id')
        user.data['reply_variable'] = reply_var
        user.save()

        text = text.replace(reply_str, '')

    return text
