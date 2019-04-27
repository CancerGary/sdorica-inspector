import hashlib
import os
import time
import traceback
from enum import Enum

import requests
import unitypack
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.six import BytesIO
from rest_framework import serializers
from django.core.files.storage import default_storage
from . import imperium_reader, ab_utils


class ImperiumType(Enum):
    unknown = 0
    gamedata = 1
    android = 2
    androidExp = 3
    localization = 4
    charAssets = 5
    settings = 6


imperium_type_id_to_name = {itype.value: itype.name for itype in ImperiumType}


class GameVersion(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)


class Imperium(models.Model):
    game_version = models.ForeignKey(GameVersion, related_name='imperiums', on_delete=models.CASCADE,
                                     null=True)  # maybe change delete mode here ?
    create_time = models.DateTimeField(default=timezone.now)
    type_id = models.IntegerField(default=0, choices=[(itype.value, itype.name) for itype in ImperiumType])
    name = models.CharField(max_length=100)
    md5 = models.CharField(max_length=32)
    uuid = models.UUIDField(null=True)
    celery_task_id = models.UUIDField(null=True)
    finished = models.BooleanField(default=False)

    def get_filename(self):
        return os.path.join(os.path.join(settings.INSPECTOR_DATA_ROOT, 'imperium', self.md5))

    def load_data(self):
        filename = self.get_filename()
        if os.path.exists(filename):
            pass
        elif self.uuid:
            if not self.download_data_by_uuid():
                return {'Puggi': "Unknown type, can't fetch"}
        else:
            return {'Puggi': 'File is missing.'}
        return imperium_reader.handle_file(open(self.get_filename(), 'rb'))

    def save_data(self, stream):
        self.md5 = hashlib.md5(stream.read()).hexdigest()
        default_storage.save(self.get_filename(), content=stream)

    def download_data_by_uuid(self):
        if self.type_id != 0:
            url = 'https://sdorica.rayark.download/{type}/client_gamedata/{uuid}/default/gamedata'.format(
                type=imperium_type_id_to_name.get(self.type_id), uuid=self.uuid)
            # TODO: check url exists
            self.save_data(BytesIO(requests.get(url, timeout=3).content))
            self.save()
            return True
        else:
            return False


class AssetBundle(models.Model):
    md5 = models.CharField(max_length=32, db_index=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200, null=True)
    imperiums = models.ManyToManyField(Imperium)

    def load_unitypack(self):
        return unitypack.load(open(os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle', self.md5), 'rb'))

    def get_containers(self):
        try:
            bundle = self.load_unitypack()
            return ab_utils.get_containers_from_ab(bundle)
        except RuntimeError:
            return {}

    def get_mixed_containers(self):
        # path_id has two types: only a path_id number (for container)
        # or two numbers (asset_index and path_id) joined by a `:` (for multi assets)

        # path_id maybe overflow in JavaScript
        result = {v['asset'].object.path_id: {'name': k, 'type': v['asset'].object.type} for k, v in
                  self.get_containers().items()}
        # result.update(
        #     {i[1]: {'name': i[0], 'type': i[5], 'asset_index': i[4]} for i in self.get_object().get_asset_objects()})
        result.update(
            {':'.join(map(str, (i.asset_index, i.path_id))): {'name': i.unityobject.name, 'type': i.unityobject.type}
             for i
             in self.unityobjectrelationship_set.all()})
        return result

    def get_unity_object_by_path_id(self, asset_index, path_id):
        data = None
        info = None
        bundle = self.load_unitypack()
        if asset_index:
            if asset_index < len(bundle.assets):
                info = bundle.assets[asset_index].objects[path_id]
                data = bundle.assets[asset_index].objects[path_id].read()
        else:
            for asset in bundle.assets:
                if asset.objects.get(path_id):
                    info = asset.objects[path_id]
                    data = asset.objects[path_id].read()
                    break
        return info, data

    def get_unity_object_by_name(self, name):
        for path_id, d in self.get_mixed_containers().items():
            o_name = d['name']
            if (o_name == name):
                return self.get_unity_object_by_path_id(*ab_utils.split_path_id(path_id))
        return None, None

    def get_asset_objects(self):
        try:
            bundle = self.load_unitypack()
            return ab_utils.get_objects_from_ab(bundle)
        except RuntimeError:
            return {}


class Container(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    asset_bundles = models.ManyToManyField(AssetBundle)


class UnityObject(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    data_hash = models.CharField(max_length=32)
    db_hash = models.CharField(max_length=32, db_index=True)  # calc from data_crc32 and name
    asset_bundles = models.ManyToManyField(AssetBundle, through='UnityObjectRelationship')
    type = models.CharField(max_length=30)


class UnityObjectRelationship(models.Model):
    assetbundle = models.ForeignKey(AssetBundle, on_delete=models.CASCADE)
    unityobject = models.ForeignKey(UnityObject, on_delete=models.CASCADE)
    path_id = models.BigIntegerField()
    asset_index = models.IntegerField(null=True)  # for multi assets


class ConvertRule(models.Model):
    pattern = models.CharField(max_length=100)
    text = models.TextField(null=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    discord_id = models.CharField(max_length=30, null=True)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance).save()


class DiscordInvite(models.Model):
    discord_id = models.CharField(max_length=30, db_index=True)


class ViewerJS(models.Model):
    javascript = models.TextField()
    unity_type = models.CharField(max_length=40, unique=True)


# class SpineData(models.Model):
#     skeleton = models.CharField(max_length=100)
#     atlas = models.CharField(max_length=100)
#     images = models.TextField()

class GameVersionSerializer(serializers.HyperlinkedModelSerializer):
    imperiums = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='imperium-detail')

    class Meta:
        model = GameVersion
        fields = ('url', 'name', 'create_time', 'id', 'imperiums')


class ImperiumSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    type_id = serializers.ChoiceField(choices=[(itype.value, itype.name) for itype in ImperiumType])
    game_version = serializers.PrimaryKeyRelatedField(queryset=GameVersion.objects.all())
    upload_file = serializers.FileField(write_only=True, required=False)
    create_time = serializers.DateTimeField(default=timezone.now)
    uuid = serializers.UUIDField(required=False)
    md5 = serializers.CharField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='imperium-detail')
    celery_task_id = serializers.UUIDField(read_only=True)
    finished = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        i = Imperium.objects.create(name=validated_data['name'], type_id=validated_data['type_id'],
                                    game_version=validated_data['game_version'],
                                    md5='0' * 32, uuid=validated_data.get('uuid'),
                                    create_time=validated_data['create_time'])
        if validated_data.get('upload_file'):
            i.save_data(validated_data.get('upload_file').open())
        i.save()
        return i

    def update(self, instance, validated_data):
        if validated_data.get('upload_file'):
            instance.save_data(validated_data.get('upload_file').open())
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_upload_file(self, value):
        try:
            # print(value)
            if value:  # InMemoryUploadedFile
                imperium_reader.handle_file(value.open())
                i = Imperium.objects.filter(md5=hashlib.md5(value.open().read()).hexdigest()).first()
                if i:
                    raise serializers.ValidationError("Imperium exists. ( id={} , name={} )".format(i.id, i.name))
        except imperium_reader.ImperiumHandleError:
            raise serializers.ValidationError("Not a readable imperium file")
        return value

    def validate_uuid(self, value):
        try:
            # print(value)
            if value:
                i = Imperium.objects.filter(uuid=value).first()
                if i and (not i == self.instance):
                    raise serializers.ValidationError("Imperium exists. ( id={} , name={} )".format(i.id, i.name))
                if self.initial_data.get('type_id') != '0':  # not unknown
                    url = 'https://sdorica.rayark.download/{type}/client_gamedata/{uuid}/default/gamedata' \
                        .format(type=imperium_type_id_to_name.get(int(self.initial_data.get('type_id'))), uuid=value)
                    # print(url,requests.head(url,timeout=3).status_code)
                    if requests.head(url, timeout=3).status_code != 200:
                        raise RuntimeError
        except RuntimeError:
            # traceback.print_exc()
            raise serializers.ValidationError("Can't fetch the file by the UUID")
        return value


class ImperiumDiffSerializer(serializers.Serializer):
    old = serializers.PrimaryKeyRelatedField(queryset=Imperium.objects.all())
    new = serializers.PrimaryKeyRelatedField(queryset=Imperium.objects.all())
    show_type = serializers.BooleanField(required=False, default=False)
    show_index = serializers.BooleanField(required=False, default=True)
    cell_lines = serializers.BooleanField(required=False, default=False)
    expand_lines = serializers.IntegerField(required=False,default=0)

    def validate(self, data):
        if data['old'].type_id != data['new'].type_id:
            raise serializers.ValidationError("must be same type")
        return data


class ImperiumABDiffSerializer(ImperiumDiffSerializer):
    def validate(self, data):
        super(ImperiumABDiffSerializer, self).validate(data)
        for side in ['old', 'new']:
            if data[side].type_id not in [ImperiumType.android.value, ImperiumType.androidExp.value]:
                raise serializers.ValidationError("{} must be asset bundle list.".format(side))
            if not data[side].finished:
                raise serializers.ValidationError("{} haven't been handled yet.".format(side))
        return data


class ConvertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConvertRule
        fields = ('id', 'pattern', 'text')


class ViewerJSSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewerJS
        fields = ('id', 'javascript', 'unity_type')


class AssetBundleSerializer(serializers.ModelSerializer):
    imperiums = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = AssetBundle
        fields = ('name', 'md5', 'url', 'imperiums')


class AssetBundleSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetBundle
        fields = ('name', 'md5')


class ContainerSerializer(serializers.ModelSerializer):
    asset_bundles = AssetBundleSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Container
        fields = ('id', 'name', 'asset_bundles')


class UnityObjectSerializer(serializers.ModelSerializer):
    asset_bundles = AssetBundleSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Container
        fields = ('id', 'name', 'asset_bundles')
