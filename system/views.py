from django.shortcuts import render
from system.models import Part, Page
from rest_framework import viewsets
from system.serializers import PartSerializer, PageSerializer


class PartViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Parts to be viewed or edited.
    """
    queryset = Part.objects.all()
    serializer_class = PartSerializer


class PageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Pages to be viewed or edited.
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
