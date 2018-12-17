from django.db import models
from rest_framework import serializers

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
    game_version = models.ForeignKey(GameVersion,on_delete=models.CASCADE,null=True) # maybe change delete mode here ?
    create_time = models.DateTimeField(auto_now_add=True)
    type_id = models.IntegerField(default=ImperiumType.unknown)
    name = models.CharField(max_length=100)

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
    class Meta:
        model = GameVersion
        fields = ('url', 'name', 'create_time', 'pk')
