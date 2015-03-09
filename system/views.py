from __future__ import unicode_literals

from rest_framework import viewsets

from system.models import Variable
from system.serializers import VariableSerializer


class VariableViewSet(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
