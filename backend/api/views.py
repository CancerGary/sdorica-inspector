import os

from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from rest_framework import viewsets,mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.api import imperium_reader
from .models import GameVersion, GameVersionSerializer, Imperium, ImperiumSerializer,ImperiumDiffSerializer
import hashlib

# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name='index.html'))


class GameVersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows game versions to be viewed or edited.
    """
    queryset = GameVersion.objects.all()
    serializer_class = GameVersionSerializer


class ImperiumViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows imperiums to be viewed or edited.
    """
    queryset = Imperium.objects.all()
    serializer_class = ImperiumSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('game_version', 'type_id')

    @action(detail=True)
    def unpack(self,request, *args, **kwargs):
        imperium = self.get_object()
        return Response(imperium.load_data())

    @action(detail=False,methods=['GET'])
    def diff(self, request):
        serializer = ImperiumDiffSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
        # print(serializer.validated_data)
            return Response(imperium_reader.c_diff(serializer.validated_data['old'].load_data(),
                                                   serializer.validated_data['new'].load_data()))