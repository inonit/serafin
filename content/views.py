# coding: utf-8
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from system.models import Part, Page


def part(request, part_id=None):

    part = get_object_or_404(Part, id=part_id)
    context = {
        'program': 'SERAF Røykeslutt',
        'title': part.title,
        'pages': part.page_set.all(),
    }

    return render(request, 'part.html', context)


def page(request, page_id=None):

    page = get_object_or_404(Page, id=page_id)
    context = {
        'program': 'SERAF Røykeslutt',
        'title': page.title,
        'pagelets': page.data,
    }

    return render(request, 'page.html', context)


def design(request):

    context = {
        'program': 'SERAF Røykeslutt',
        'title': 'Designtest',
    }

    return render(request, 'design.html', context)
