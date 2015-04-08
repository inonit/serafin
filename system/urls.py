from __future__ import unicode_literals

from django.conf.urls import patterns, url, include
from rest_framework import routers

from system.views import VariableViewSet, VariableSearchViewSet


router = routers.DefaultRouter()
router.register(r'variables/search', VariableSearchViewSet)
router.register(r'variables', VariableViewSet)

urlpatterns = patterns(
    '',
    url(r'', include(router.urls)),
)

