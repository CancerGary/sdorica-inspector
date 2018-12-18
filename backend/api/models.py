import hashlib
import os
from django.conf import settings
from django.db import models
from rest_framework import serializers
from django.core.files.storage import default_storage
from . import imperium_reader

class ImperiumType:
    unknown = 0
    gamedata = 1
    android = 2
    androidExp = 3
    localization = 4

class TranslateLanguage:
    english = 0

class GameVersion(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)

class Imperium(models.Model):
    game_version = models.ForeignKey(GameVersion,related_name='imperiums',on_delete=models.CASCADE,null=True) # maybe change delete mode here ?
    create_time = models.DateTimeField(auto_now_add=True)
    type_id = models.IntegerField(default=ImperiumType.unknown)
    name = models.CharField(max_length=100)
    md5 = models.CharField(max_length=32)

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
    type_id = serializers.IntegerField()
    game_version = serializers.PrimaryKeyRelatedField(queryset=GameVersion.objects.all())
    upload_file = serializers.FileField(write_only=True,allow_null=True)
    create_time = serializers.DateTimeField(read_only=True)
    md5 = serializers.CharField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='imperium-detail')

    def create(self, validated_data):
        if validated_data.get('upload_file'):
            md5 = hashlib.md5(validated_data.get('upload_file').open().read()).hexdigest()
            default_storage.save(os.path.join(settings.INSPECTOR_DATA_ROOT,'imperium',md5),content=validated_data['upload_file'])
        else:
            md5='0'*32
        return Imperium.objects.create(name=validated_data['name'],type_id=validated_data['type_id'],
                                       game_version=validated_data['game_version'],
                                       md5=md5)

    def update(self, instance, validated_data):
        if validated_data.get('upload_file'):
            instance.md5 = hashlib.md5(validated_data.get('upload_file').open().read()).hexdigest()
            default_storage.save(os.path.join(settings.INSPECTOR_DATA_ROOT,'imperium',instance.md5),content=validated_data['upload_file'])
        else:
            # instance.name=validated_data.get('name',instance.name)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
        instance.save()
        return instance


    def validate_upload_file(self, value):
        try:
            # print(value)
            if value:
                imperium_reader.handle_file(value)
        except:
            raise serializers.ValidationError("Not a readable imperium file")
        return value
