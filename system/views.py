# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from rest_framework import viewsets

from .models import Variable
from .serializers import VariableSerializer
from .filters import VariableSearchFilter


class VariableViewSet(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer


class VariableSearchViewSet(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
    filter_backends = [VariableSearchFilter]
    search_fields = ["name", "display_name"]


