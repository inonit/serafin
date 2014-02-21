from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.shortcuts import render
from content.models import Text, Form, Image, Video, Audio, File


def page_test(request):

    context = {
        'page_title': 'Page test',
        'pagelets': [
            Text.objects.get(id=1),
            #Form.objects.get(id=1),
            #Image.objects.get(id=1),
            #Video.objects.get(id=1),
            #Audio.objects.get(id=1),
            #File.objects.get(id=1),
        ]
    }

    return render(request, 'page.html', context)
