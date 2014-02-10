from django.shortcuts import render

def page_test(request):

    context = {
        'pagelets': [

        ]
    }

    return render(request, 'page.html', context)
