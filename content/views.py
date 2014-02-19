from django.shortcuts import render

def page_test(request):

    context = {
        'page_title': 'Page test',
        'pagelets': [
            Text.objects.get(id=1),
            Form.objects.get(id=1),
            Image.objects.get(id=1),
            Video.objects.get(id=1),
            Audio.objects.get(id=1),
            File.objects.get(id=1),
        ]
    }

    return render(request, 'page.html', context)
