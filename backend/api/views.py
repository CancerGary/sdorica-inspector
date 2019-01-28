import os

from celery.result import AsyncResult
from django.shortcuts import redirect, render
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.api import imperium_reader
from .models import GameVersion, GameVersionSerializer, Imperium, ImperiumSerializer, ImperiumDiffSerializer, \
    ImperiumType, ImperiumABDiffSerializer
import hashlib

from . import tasks
from .celery import app as celery_app

# Serve Vue Application
index_view = login_required(never_cache(TemplateView.as_view(template_name='index.html')))

from rest_framework.authentication import SessionAuthentication, BasicAuthentication


# disable csrf check
class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


# login page
def login_view(request):
    alert_msg = ""
    if request.method == 'POST' and request.POST.get('username') and request.POST.get('password'):
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return redirect('/')
        alert_msg = 'Invalid username or password. Maybe you can contact Puggi for help.'
    return render(request, template_name='login.html', context={'alert': alert_msg})


class GameVersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows game versions to be viewed or edited.
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    queryset = GameVersion.objects.all()
    serializer_class = GameVersionSerializer


class ImperiumViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows imperiums to be viewed or edited.
    """
    queryset = Imperium.objects.all()
    serializer_class = ImperiumSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('game_version', 'type_id','finished')

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=True)
    def unpack(self, request, *args, **kwargs):
        imperium = self.get_object()
        return Response(imperium.load_data())

    @action(detail=True)
    def download_ab(self, request, *args, **kwargs):
        imperium = self.get_object()
        if imperium.type_id in [ImperiumType.android.value, ImperiumType.androidExp.value]:
            if imperium.finished:
                return Response('Finished')
            elif imperium.celery_task_id:
                # TODO: retrieve progress detail
                return Response('Handling')
            else:
                imperium.celery_task_id = tasks.ab_list_task.delay(imperium.id).id
                imperium.save()
                return Response('Starting')
        else:
            return Response('Bad type')

    @action(detail=False, methods=['GET'])
    def diff(self, request):
        serializer = ImperiumDiffSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            # print(serializer.validated_data)
            return Response(imperium_reader.c_diff(serializer.validated_data['old'].load_data(),
                                                   serializer.validated_data['new'].load_data()))

    @action(detail=False, methods=['GET'])
    def ab_diff(self, request):
        serializer = ImperiumABDiffSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            # print(serializer.validated_data)
            left = serializer.validated_data['old'].assetbundle_set.all()
            right = serializer.validated_data['new'].assetbundle_set.all()
            # compare by asset bundle name
            d_left = {i.name: i for i in left}
            d_right = {i.name: i for i in right}
            dlk = d_left.keys()
            drk = d_right.keys()
            delete = {k: {'md5': d_left[k].md5,
                          'data': sorted([i['name'] for i in d_left[k].container_set.values('name')])}
                      for k in dlk - drk}
            add = {k: {'md5': d_right[k].md5,
                       'data': sorted([i['name'] for i in d_right[k].container_set.values('name')])}
                   for k in drk - dlk}
            # only size changed
            nochange = dict()
            change = dict()
            for k in dlk & drk:
                cl = {i['name'] for i in d_left[k].container_set.values('name')}
                cr = {i['name'] for i in d_right[k].container_set.values('name')}
                if (cl != cr):
                    change[k] = {'delete': cl - cr, 'add': cr - cl,'md5' :(d_left[k].md5,d_right[k].md5)}
                elif d_left[k].md5 != d_right[k].md5:
                    nochange[k] = (d_left[k].md5 , d_right[k].md5)
            return Response({'delete': delete, 'add': add, 'change': change,'nochange':nochange})
