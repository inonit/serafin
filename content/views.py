from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from django.shortcuts import render
from system.models import Page


def design_test(request):

    context = {}

    return render(request, 'design.html', context)

@login_required()
def page_test(request):

    context = {
        'page_title': 'Page test',
    }

    return render(request, 'page.html', context)
