from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from django.shortcuts import render, get_object_or_404
from system.models import Part, Page


def content_test(request):

    part = get_object_or_404(Part, title='Dag 1')
    context = {
        'title': part.title,
        'pages': part.page_set.all(),
    }

    return render(request, 'part.html', context)


def design_test(request):

    context = {
    }

    return render(request, 'design.html', context)


def page_test(request):

    page = get_object_or_404(Page, id=3)
    context = {
        'page_title': page.title,
        'pagelets': page.data,
    }

    return render(request, 'page.html', context)

