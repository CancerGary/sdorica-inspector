import hashlib
import os
import time
import traceback
from enum import Enum

import requests
from django.conf import settings
from django.db import models
from django.utils.six import BytesIO
from rest_framework import serializers
from django.core.files.storage import default_storage
from . import imperium_reader

class ImperiumType(Enum):
    unknown = 0
    gamedata = 1
    android = 2
    androidExp = 3
    localization = 4

imperium_type_id_to_name={itype.value:itype.name for itype in ImperiumType}
class TranslateLanguage:
    english = 0

class GameVersion(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)

class Imperium(models.Model):
    game_version = models.ForeignKey(GameVersion,related_name='imperiums',on_delete=models.CASCADE,null=True) # maybe change delete mode here ?
    create_time = models.DateTimeField(auto_now_add=True)
    type_id = models.IntegerField(default=0,choices=[(itype.value,itype.name) for itype in ImperiumType])
    name = models.CharField(max_length=100)
    md5 = models.CharField(max_length=32)
    uuid = models.UUIDField(null=True)

    def get_filename(self):
        return os.path.join(os.path.join(settings.INSPECTOR_DATA_ROOT, 'imperium', self.md5))

    def load_data(self):
        filename = self.get_filename()
        if os.path.exists(filename):
            pass
        elif self.uuid:
            self.download_data_by_uuid()
        else:
            return {'Puggi':'File is missing.'}
        return imperium_reader.handle_file(open(self.get_filename(), 'rb'))

    def save_data(self, stream):
        self.md5 = hashlib.md5(stream.read()).hexdigest()
        default_storage.save(self.get_filename(),content=stream)

    def download_data_by_uuid(self):
        url = 'https://sdorica.rayark.download/{type}/client_gamedata/{uuid}/default/gamedata'.format(
            type=imperium_type_id_to_name.get(self.type_id), uuid=self.uuid)
        # TODO: check url exists
        self.save_data(BytesIO(requests.get(url,timeout=3).content))
        self.save()

class AssetBundle(models.Model):
    md5 = models.CharField(max_length=32)
    name = models.CharField(max_length=100)
    imperium = models.ManyToManyField(Imperium)

class Asset(models.Model):
    name = models.CharField(max_length=100)
    asset_bundle = models.ForeignKey(AssetBundle,on_delete=models.CASCADE)

class AssetObject(models.Model):
    name = models.CharField(max_length=100,null=True)
    path_id = models.IntegerField()
    type_id = models.IntegerField()
    type_name = models.CharField(max_length=40)
    # maybe save Object._obj data
    asset = models.ForeignKey(Asset,on_delete=models.CASCADE)

class TranslateTable(models.Model):
    key = models.CharField(max_length=40)
    text = models.TextField(null=True)
    language =models.IntegerField(default=0)

class GameVersionSerializer(serializers.HyperlinkedModelSerializer):
    imperiums = serializers.HyperlinkedRelatedField(many=True,read_only=True,view_name='imperium-detail')
    class Meta:
        model = GameVersion
        fields = ('url', 'name', 'create_time', 'id','imperiums')

class ImperiumSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    type_id = serializers.ChoiceField(choices=[(itype.value,itype.name) for itype in ImperiumType])
    game_version = serializers.PrimaryKeyRelatedField(queryset=GameVersion.objects.all())
    upload_file = serializers.FileField(write_only=True,required=False)
    create_time = serializers.DateTimeField(read_only=True)
    uuid = serializers.UUIDField(required=False)
    md5 = serializers.CharField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='imperium-detail')

    def create(self, validated_data):
        i = Imperium.objects.create(name=validated_data['name'], type_id=validated_data['type_id'],
                                game_version=validated_data['game_version'],
                                md5='0'*32,uuid=validated_data.get('uuid'))
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
            if value: # InMemoryUploadedFile
                imperium_reader.handle_file(value.open())
        except:
            raise serializers.ValidationError("Not a readable imperium file")
        return value

    def validate_uuid(self, value):
        try:
            # print(value)
            if value:
                url = 'https://sdorica.rayark.download/{type}/client_gamedata/{uuid}/default/gamedata'.format(type=imperium_type_id_to_name.get(int(self.initial_data.get('type_id'))),uuid=value)
                # print(url,requests.head(url,timeout=3).status_code)
                if requests.head(url,timeout=3).status_code!=200:
                    raise Exception
        except:
            traceback.print_exc()
            raise serializers.ValidationError("Can't fetch the file by the UUID")
        return value

class ImperiumDiffSerializer(serializers.Serializer):
    old = serializers.PrimaryKeyRelatedField(queryset=Imperium.objects.all())
    new = serializers.PrimaryKeyRelatedField(queryset=Imperium.objects.all())
