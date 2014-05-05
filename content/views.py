from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from filer.models import File, Image
from serafin.utils import JSONResponse, user_data_replace
from system.models import Part, Page
import json
import mistune


@login_required
def get_part(request):

    if request.is_ajax():
        return get_page(request)

    user_data = request.user.data
    data = {
        'user_data': user_data
    }

    # TODO: run system and supply data
    # TODO: get current Part object back from system
    #part = system.something(request.user, data)

    # preview support
    part_id = request.GET.get('part_id')
    if request.user.is_staff and part_id:
        part = Part.objects.get(id=part_id)

    context = {
        'program': part.program,
        'api': reverse('content_api'),
    }

    return render(request, 'part.html', context)


@login_required
def get_page(request):

    data = {}

    if request.method == 'POST':
        post_data = json.loads(request.body)
        data.update({
            'post_data': post_data
        })

    user_data = request.user.data
    data.update({
        'user_data': user_data
    })

    # TODO: run system and supply data
    # TODO: get Page object back from system
    #page = system.something(request.user, data)

    # preview support
    page_id = request.GET.get('page_id')
    if request.user.is_staff:
        page = Page.objects.get(id=page_id)

    for pagelet in page.data:
        try:
            if pagelet['content_type'] == 'text':
                replaced = user_data_replace(
                    request.user,
                    pagelet['content']['text']
                )
                pagelet['content']['html'] = mistune.markdown(replaced)
        except:
            continue

    response = {
        'title': page.title,
        'data': page.data,
    }

    return JSONResponse(response)


@staff_member_required
def api_filer_file(request, content_type=None, file_id=None):

    if content_type == 'image':
        filer_file = get_object_or_404(Image, id=file_id)
    else:
        filer_file = get_object_or_404(File, id=file_id)

    response = {
        'id': filer_file.id,
        'url': filer_file.url,
        'thumbnail': filer_file.icons['48'],
        'description': filer_file.original_filename,
    }

    return JSONResponse(response)
