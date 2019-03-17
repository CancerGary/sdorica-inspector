import errno
import os
import pickle
import socket
from collections import OrderedDict
from io import BytesIO

import redis
from PIL import Image
from celery.result import AsyncResult
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
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
from unitypack.engine.texture import TextureFormat

from backend.api import imperium_reader, ab_utils
from .models import GameVersion, GameVersionSerializer, Imperium, ImperiumSerializer, ImperiumDiffSerializer, \
    ImperiumType, ImperiumABDiffSerializer, ConvertRule, ConvertRuleSerializer, Container, ContainerSerializer, \
    AssetBundleSerializer, AssetBundle, ViewerJS, ViewerJSSerializer
import hashlib

from . import tasks
from .celery import app as celery_app

from . import ETC2ImagePlugin
import subprocess

# Serve Vue Application
index_view = login_required(never_cache(TemplateView.as_view(template_name='index.html')))

from rest_framework.authentication import SessionAuthentication, BasicAuthentication

cache_dir = os.makedirs(os.path.join(settings.INSPECTOR_DATA_ROOT, 'object_cache'), exist_ok=True)
os.makedirs(os.path.join(settings.STATIC_ROOT, 'audio'), exist_ok=True)


def handle_image_data(object_data):
    data_md5 = hashlib.md5(object_data.image_data).hexdigest()
    cache_file_path = os.path.join(settings.INSPECTOR_DATA_ROOT, 'object_cache', data_md5)
    if os.path.exists(cache_file_path):
        return open(cache_file_path, 'rb').read()
    else:
        args = ["RGB" if object_data.format.pixel_format in ("RGB", "RGB;16") else (
            "RGB" if (object_data.format == TextureFormat.ETC2_RGB) else "RGBA"),
                (object_data.width, object_data.height),
                object_data.image_data, 'etc2',
                (object_data.format.value, object_data.format.pixel_format,)]
        if settings.INSPECTOR_PYPY_PATH:
            open(cache_file_path + '.pypy.data', 'wb').write(args[2])
            args[2] = ''
            pickle.dump(args, open(cache_file_path + '.pypy.pkl', 'wb'))
            p = subprocess.Popen([settings.INSPECTOR_PYPY_PATH,
                                  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sub_pypy.py'),
                                  cache_file_path])
            p.communicate()
            if p.returncode == 0:
                os.remove(cache_file_path + '.pypy.data')
                os.remove(cache_file_path + '.pypy.pkl')
                return open(cache_file_path, 'rb').read()
        else:
            f = BytesIO()
            Image.frombytes(*args).transpose(Image.FLIP_TOP_BOTTOM).save(f, 'png')
            open(cache_file_path, 'wb').write(f.getvalue())
            return f.getvalue()


# disable csrf check
class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class GameVersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows game versions to be viewed or edited.
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.DjangoModelPermissions,)

    queryset = GameVersion.objects.all()
    serializer_class = GameVersionSerializer


class ImperiumViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows imperiums to be viewed or edited.
    """
    queryset = Imperium.objects.all()
    serializer_class = ImperiumSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('game_version', 'type_id', 'finished')

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.DjangoModelPermissions,)

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
    def diff_text(self, request):
        serializer = ImperiumDiffSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            # print(serializer.data)
            return Response(imperium_reader.c_diff_text(serializer.validated_data['old'].load_data(),
                                                        serializer.validated_data['new'].load_data(),
                                                        show_type=serializer.validated_data.get('show_type'),
                                                        show_index=serializer.validated_data.get('show_index'),
                                                        cell_cep='\n' if serializer.validated_data.get(
                                                            'cell_lines') else ', '))

    @action(detail=False, methods=['GET'])
    def ab_diff(self, request):
        list_vl = lambda q: list(q.values_list('name', flat=True).order_by('name'))
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
                          'data': list_vl(d_left[k].container_set) + list_vl(d_left[k].unityobject_set)}
                      for k in dlk - drk}
            add = {k: {'md5': d_right[k].md5,
                       'data': list_vl(d_right[k].container_set) + list_vl(d_right[k].unityobject_set)}
                   for k in drk - dlk}
            # only size changed
            nochange = dict()
            change = dict()
            for k in dlk & drk:
                if d_left[k].md5 == d_right[k].md5: continue  # skip the query
                cl = {i['name'] for i in d_left[k].container_set.values('name')}
                cr = {i['name'] for i in d_right[k].container_set.values('name')}
                ol = {(i['name'], i['db_hash']) for i in d_left[k].unityobject_set.values('name', 'db_hash')}
                or_ = {(i['name'], i['db_hash']) for i in d_right[k].unityobject_set.values('name', 'db_hash')}
                if cl == cr and ol == or_:
                    nochange[k] = (d_left[k].md5, d_right[k].md5)
                else:
                    change[k] = {'delete': list(cl - cr) + [i[0] for i in ol - or_],
                                 'add': list(cr - cl) + [i[0] for i in or_ - ol],
                                 'md5': (d_left[k].md5, d_right[k].md5)}
            return Response({'delete': delete, 'add': add, 'change': change, 'nochange': nochange})


class ConvertRuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows convert rules to be viewed or edited.
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.DjangoModelPermissions,)

    queryset = ConvertRule.objects.all()
    serializer_class = ConvertRuleSerializer


class ContainerViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows containers to be viewed or edited.
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.DjangoModelPermissions,)

    queryset = Container.objects.all()

    @action(detail=False, methods=['GET'])
    def search(self, request):
        if not request.query_params.get('query'):
            return Response('Query is too short')
        result = self.get_queryset()
        for i in request.query_params.get('query').split(' '):
            result = result.filter(name__contains=i)
        return Response(ContainerSerializer(result, many=True).data)


class AssetBundleViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows containers to be viewed or edited.
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.DjangoModelPermissions,)

    queryset = AssetBundle.objects.all()
    serializer_class = AssetBundleSerializer
    lookup_field = 'md5'

    def retrieve(self, request, md5=None):
        try:
            return Response(AssetBundleSerializer(self.queryset.get(md5=md5)).data)
        except AssetBundle.DoesNotExist:
            return Response(AssetBundleSerializer(get_object_or_404(self.queryset, pk=md5)).data)

    @action(detail=True)
    def containers(self, request, md5=None):
        # path_id maybe overflow in JavaScript
        result = {v['asset'].object.path_id: {'name': k, 'type': v['asset'].object.type} for k, v in
                  self.get_object().get_containers().items()}
        # TODO: read from database
        result.update({i[1]:{'name':i[0],'type':i[5]} for i in self.get_object().get_asset_objects()})
        return Response(result)

    # TODO: add asset_index for multi assets
    @action(detail=True, url_path='containers/(?P<path_id>-?[0-9]+)/?')
    def containers_retrieve(self, request, md5=None, path_id=None, *args, **kwargs):
        path_id = int(path_id)
        data = None
        bundle = self.get_object().load_unitypack()
        for asset in bundle.assets:
            if asset.objects.get(path_id):
                data = asset.objects[path_id].read()
                break
        if data is None:
            raise Http404
        else:
            # TODO: maybe bugs
            d = ab_utils.strip_pointers(data) if type(data) is OrderedDict else ab_utils.strip_pointers(data._obj)
            # remove too long base64 data
            if d.get('image data'): d.pop('image data')
            return Response(d)

    @action(detail=True, url_path='containers/(?P<path_id>-?[0-9]+)/data')
    def containers_data(self, request, md5=None, path_id=None, *args, **kwargs):
        '''
        `/data` url is designed for object types already in Unity3D. For customized types (such as `DialogAsset` ),
        using JavaScript at frontend is better.
        '''
        path_id = int(path_id)
        data = None
        info = None
        bundle = self.get_object().load_unitypack()
        for asset in bundle.assets:
            if asset.objects.get(path_id):
                info = asset.objects[path_id]
                data = asset.objects[path_id].read()
                break
        if data is None:
            raise Http404
        else:
            if info.type == 'Texture2D':
                return HttpResponse(handle_image_data(data), content_type="image/png")
            elif info.type == 'Sprite':
                rect = data.rd['textureRect']
                # load texture first, then crop the area
                img = Image.open(BytesIO(handle_image_data(data.rd['texture'].object.read()))) \
                    .transpose(Image.FLIP_TOP_BOTTOM) \
                    .crop(box=(rect['x'], rect['y'], rect['x'] + rect['width'], rect['y'] + rect['height'])) \
                    .transpose(Image.FLIP_TOP_BOTTOM)
                f = BytesIO()
                img.save(f, 'png')
                return HttpResponse(f.getvalue(), content_type="image/png")
            elif info.type == 'AudioClip':
                filename = "%s,%s" % (md5, path_id)
                filepath = os.path.join(settings.STATIC_ROOT, 'audio', filename)
                if not os.path.exists(filepath):
                    cache = ab_utils.handle_fsb(data.data)
                    open(filepath, 'wb').write(cache)
                return redirect('/static/audio/' + filename)
            else:
                return Http404


class ViewerJSViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows viewer javascript to be viewed or edited.
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.DjangoModelPermissions,)

    queryset = ViewerJS.objects.all()
    serializer_class = ViewerJSSerializer
    lookup_field = 'unity_type'


def get_dir_size(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


def get_git_master_hash(git_base):
    master_path = os.path.join(git_base, 'refs/heads/master')
    if os.path.exists(master_path):
        return open(master_path).read().strip()
    return None


class StatusViewSet(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def list(self, request):
        redis_online = True
        try:
            result = redis.Redis(socket_connect_timeout=1).time()
        except redis.exceptions.RedisError:
            redis_online = False
        return Response({'asset_bundles': AssetBundle.objects.all().count(),
                         'imperiums': Imperium.objects.all().count(),
                         'containers': Container.objects.all().count(),
                         'data_size': get_dir_size(settings.INSPECTOR_DATA_ROOT),
                         'redis': redis_online,
                         'users': User.objects.all().count(),
                         'master_hash': get_git_master_hash(os.path.join(settings.BASE_DIR, '.git'))})
