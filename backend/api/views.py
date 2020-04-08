import json
import hashlib
import json
import os
import pickle
import re
import subprocess
import uuid
from collections import OrderedDict
from io import BytesIO
from zipfile import ZipFile

import redis
from PIL import Image
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.http.response import FileResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from pydub import AudioSegment
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from unitypack.engine.texture import TextureFormat

from backend.api import imperium_reader, ab_utils, skel2json
from . import tasks
from .models import GameVersion, GameVersionSerializer, Imperium, ImperiumSerializer, ImperiumDiffSerializer, \
    ImperiumType, ImperiumABDiffSerializer, ConvertRule, ConvertRuleSerializer, Container, ContainerSerializer, \
    AssetBundleSerializer, AssetBundle, ViewerJS, ViewerJSSerializer, UnityObject, UnityObjectSerializer

# Serve Vue Application
index_view = login_required(never_cache(TemplateView.as_view(template_name='index.html')))

from rest_framework.authentication import SessionAuthentication, BasicAuthentication

cache_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'object_cache')
os.makedirs(cache_dir, exist_ok=True)
spine_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'spine')
os.makedirs(spine_dir, exist_ok=True)
os.makedirs(os.path.join(settings.STATIC_ROOT, 'audio'), exist_ok=True)


def handle_image_data(object_data):
    try:
        f = BytesIO()
        object_data.image.transpose(Image.FLIP_TOP_BOTTOM).save(f, 'png')
        f.seek(0)
        return f
    except NotImplementedError:
        pass
    data_md5 = hashlib.md5(object_data.image_data).hexdigest()
    cache_file_path = os.path.join(settings.INSPECTOR_DATA_ROOT, 'object_cache', data_md5)
    if os.path.exists(cache_file_path):
        return open(cache_file_path, 'rb')
    else:
        # print(object_data.format,object_data.format.pixel_format)
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
                return open(cache_file_path, 'rb')
        else:
            f = BytesIO()
            Image.frombytes(*args).transpose(Image.FLIP_TOP_BOTTOM).save(f, 'png')
            open(cache_file_path, 'wb').write(f.getvalue())
            f.seek(0)
            return f


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
    queryset = Imperium.objects.all().order_by('-create_time')
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
                                                            'cell_lines') else ', ',
                                                        n=abs(serializer.validated_data.get('expand_lines'))))

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
                    change[k] = {'delete': sorted(cl - cr) + sorted([i[0] for i in ol - or_]),
                                 'add': sorted(cr - cl) + sorted([i[0] for i in or_ - ol]),
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
    permission_classes = (IsAuthenticated,)

    queryset = Container.objects.all()

    @action(detail=False, methods=['GET'])
    def search(self, request):
        if not request.query_params.get('query'):
            raise ValidationError('Query is too short')
        result = self.get_queryset()
        result_uo = UnityObject.objects.all()
        if request.query_params.get('imperium'):
            imperium = get_object_or_404(Imperium, id=request.query_params.get('imperium'))
            # result = result.select_related().filter(asset_bundles__in=imperium.assetbundle_set.get_queryset())
            # print(result.query)
        for i in request.query_params.get('query').split(' '):
            result = result.filter(name__icontains=i)
            result_uo = result_uo.filter(name__icontains=i)

        # TODO: serializer filter by imperium
        return Response(ContainerSerializer(result, many=True).data + UnityObjectSerializer(result_uo, many=True).data)

    @action(detail=False, methods=['POST'])
    def multi_search(self, request):
        queries = request.data.get('queries')
        # print(queries)
        if not isinstance(queries, list) or not all(isinstance(q, str) for q in queries):
            raise ValidationError('No queries list')

        result_list = []
        for q in queries:
            result = self.get_queryset()
            result_uo = UnityObject.objects.all()
            for i in q.split(' '):
                result = result.filter(name__icontains=i)
                result_uo = result_uo.filter(name__icontains=i)
            result_list.append(
                ContainerSerializer(result, many=True).data + UnityObjectSerializer(result_uo, many=True).data)
        return Response(result_list)


class AssetBundleViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows containers to be viewed or edited.
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = AssetBundle.objects.all()
    serializer_class = AssetBundleSerializer
    lookup_field = 'md5'

    def retrieve(self, request, md5=None):
        try:
            return Response(AssetBundleSerializer(self.queryset.get(md5=md5)).data)
        except AssetBundle.DoesNotExist:
            try:
                return Response(AssetBundleSerializer(get_object_or_404(self.queryset, pk=md5)).data)
            except ValueError:
                raise Http404

    @action(detail=True)
    def containers(self, request, md5=None):
        return Response(self.get_object().get_mixed_containers())

    @action(detail=True, url_path='containers/(?P<path_id>([0-9]+:)?-?[0-9]+)/?')
    def containers_retrieve(self, request, path_id, md5=None, *args, **kwargs):
        asset_index, path_id = ab_utils.split_path_id(path_id)
        info, data = self.get_object().get_unity_object_by_path_id(asset_index, path_id)

        if data is None:
            raise Http404
        else:
            # TODO: maybe bugs
            d = ab_utils.strip_pointers(data) if type(data) is OrderedDict else ab_utils.strip_pointers(data._obj)
            # remove too long base64 data
            if d.get('image data'): d.pop('image data')
            return Response(d)

    @action(detail=False, methods=['POST'], url_path='containers/multi_retrieve/?')
    def multi_retrieve(self, request):
        queries = request.data.get('queries')
        if not isinstance(queries, list) or not all(
                (isinstance(q, list) and len(q) == 2 and isinstance(q[0], str) and isinstance(q[1], str)) for q in
                queries):
            raise ValidationError('No queries list')
        result = []
        ab_cache = dict()
        for md5, path_id in queries:
            asset_index, path_id = ab_utils.split_path_id(path_id)
            if ab_cache.get(md5, None) is None:
                try:
                    ab_cache[md5] = AssetBundle.objects.get(md5=md5)
                except:
                    ab_cache[md5] = False
            if ab_cache[md5]:
                info, data = ab_cache[md5].get_unity_object_by_path_id(asset_index, path_id)
                if data is None:
                    result.append(None)
                else:
                    # TODO: maybe bugs
                    d = ab_utils.strip_pointers(data) if type(data) is OrderedDict else ab_utils.strip_pointers(
                        data._obj)
                    # remove too long base64 data
                    if d.get('image data'): d.pop('image data')
                    result.append(d)
            else:
                result.append(None)
        return Response(result)

    @action(detail=True, url_path='containers/(?P<path_id>([0-9]+:)?-?[0-9]+)/data')
    def containers_data(self, request, md5=None, path_id=None, *args, **kwargs):
        '''
        `/data` url is designed for object types already in Unity3D. For customized types (such as `DialogAsset` ),
        using JavaScript at frontend is better.
        '''
        asset_index, path_id = ab_utils.split_path_id(path_id)
        info, data = self.get_object().get_unity_object_by_path_id(asset_index, path_id)
        as_attachment = True if request.query_params.get('attachment') else False
        jpeg_format = True if request.query_params.get('jpeg') else False
        if data is None:
            raise Http404
        else:
            if info.type == 'Texture2D':
                name = "%s.%s" % ((data.name) if data.name else "data", 'jpg' if jpeg_format else "png")
                if jpeg_format:
                    f = BytesIO()
                    Image.open(handle_image_data(data)).convert('RGB').save(f, 'jpeg')
                    f.seek(0)
                    return FileResponse(f, as_attachment=as_attachment, filename=name)
                else:
                    return FileResponse(handle_image_data(data), as_attachment=as_attachment, filename=name)
            elif info.type == 'Sprite':
                name = "%s.%s" % ((data.name) if data.name else "data", 'jpg' if jpeg_format else "png")
                rect = data.rd['textureRect']
                # load texture first, then crop the area
                img = Image.open(handle_image_data(data.rd['texture'].object.read())) \
                    .transpose(Image.FLIP_TOP_BOTTOM) \
                    .crop(box=(rect['x'], rect['y'], rect['x'] + rect['width'], rect['y'] + rect['height'])) \
                    .transpose(Image.FLIP_TOP_BOTTOM)
                f = BytesIO()
                if jpeg_format:
                    img.convert("RGB").save(f, 'jpeg')
                else:
                    img.save(f, 'png')
                f.seek(0)
                return FileResponse(f, as_attachment=as_attachment, filename=name)
            elif info.type == 'AudioClip':
                filename = "%s,%s.mp3" % (md5, path_id)
                filepath = os.path.join(settings.STATIC_ROOT, 'audio', filename)
                if not os.path.exists(filepath):
                    AudioSegment.from_ogg(BytesIO(ab_utils.handle_fsb(data.data))).export(filepath)
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


class SpineViewSet(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    lookup_field = 'spine_uuid'
    lookup_value_regex = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'

    # def retrieve(self, request, spine_uuid=None):
    #     return Response(spine_uuid)

    def get_permissions(self):
        """
        A dummy way to fix spine-ts loadTexture `crossOrigin: "anonymous"` problem
        """
        if self.action == 'retrieve_image':
            return [AllowAny(), ]
        return super(SpineViewSet, self).get_permissions()

    def get_ab_o(self, info):
        return AssetBundle.objects.get(md5=info['md5']).get_unity_object_by_name(info['name'])

    def create(self, request):
        # skeleton
        try:
            info, skel_data = self.get_ab_o(request.data['skeleton'])
            if info.type != 'TextAsset': raise TypeError
        except Exception as e:
            raise ValidationError("skeleton data error %s" % (e))

        # atlas
        try:
            info, atlas_data = self.get_ab_o(request.data['atlas'])
            b = atlas_data.bytes
            atlas_text = (b if isinstance(b, str) else b.decode('utf8'))
            if info.type != 'TextAsset': raise TypeError
            # http://esotericsoftware.com/spine-atlas-format
            atlas_pages = re.findall('\n(.*?.png)\nsize: ?(\d+),(\d+)', atlas_text)
            # print(atlas_pages)
        except Exception as e:
            raise ValidationError("Atlas data error %s" % (e))

        # images
        if len(atlas_pages) != len(request.data['images']):
            raise ValidationError('selected wrong count of images (need %d, given %d)' % (
                len(atlas_pages), len(request.data['images'])))
        try:
            pil = []  # [(filename, resized PIL.Image)]
            for page, img_info in zip(atlas_pages, request.data['images']):
                info, texture_data = self.get_ab_o(img_info)
                if info.type != 'Texture2D': raise TypeError
                # resize by page description
                pil.append((page[0],
                            Image.open(handle_image_data(texture_data)).resize((int(page[1]), int(page[2])))))
        except Exception as e:
            raise ValidationError("Atlas data error %s" % (e))

        # write task
        try:
            task_uuid = str(uuid.uuid4())
            base = os.path.join(spine_dir, task_uuid)
            os.makedirs(base, exist_ok=True)

            # json.dump(skel_json, open(os.path.join(base, 'data.json'), 'w'))
            open(os.path.join(base, 'data.skel'), 'wb').write(skel_data.script)  # for debugging
            open(os.path.join(base, 'data.atlas'), 'w').write(atlas_text)
            for im_name, im in pil:
                im.save(open(os.path.join(base, im_name), 'wb'), 'png')
        except Exception as e:
            raise ValidationError("Final writing error %s" % (e))

        return Response({'task_uuid': task_uuid})

    def check_spine_uuid(self, spine_uuid):
        path = os.path.join(spine_dir, spine_uuid)
        if os.path.isdir(path):
            return path
        else:
            raise Http404

    def retrieve(self, request, spine_uuid):
        return Response(os.listdir(self.check_spine_uuid(spine_uuid)))

    @action(detail=True, methods=['GET'], url_path='json')
    def retrieve_json(self, request, spine_uuid=None):
        path = self.check_spine_uuid(spine_uuid)
        skel_json = skel2json.Handler(open(os.path.join(path, 'data.skel'), 'rb')).handle()
        return Response(skel_json)

    @action(detail=True, methods=['GET'], url_path='skel')
    def retrieve_skel(self, request, spine_uuid=None):
        path = self.check_spine_uuid(spine_uuid)
        return HttpResponse(open(os.path.join(path, 'data.skel'), 'rb').read())

    @action(detail=True, methods=['GET'], url_path='atlas')
    def retrieve_atlas(self, request, spine_uuid=None):
        path = self.check_spine_uuid(spine_uuid)
        return HttpResponse(open(os.path.join(path, 'data.atlas'), encoding='utf8').read())

    @action(detail=True, methods=['GET'], url_path='atlas/(?P<img_name>[^\\/:*?\"<|>]+)')
    def retrieve_image(self, request, spine_uuid=None, img_name=None):
        path = self.check_spine_uuid(spine_uuid)
        return HttpResponse(open(os.path.join(path, img_name), 'rb').read())

    @action(detail=True, methods=['GET'], url_path='zip')
    def retrieve_zip(self, request, spine_uuid=None):
        path = self.check_spine_uuid(spine_uuid)
        f = BytesIO()
        with ZipFile(f, 'w') as zipfile:
            for fn in os.listdir(path):
                if fn.endswith('.skel') or fn.endswith('.png') or fn.endswith('.atlas'):
                    zipfile.write(os.path.join(path, fn), fn)
            zipfile.writestr('data.json',
                             data=json.dumps(skel2json.Handler(open(os.path.join(path, 'data.skel'), 'rb')).handle()))
        f.seek(0)  # when being closed , it goes to end
        return FileResponse(f, as_attachment=True, filename=spine_uuid + '.zip')
