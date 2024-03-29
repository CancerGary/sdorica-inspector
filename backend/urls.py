"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from .api.views import index_view, GameVersionViewSet, ImperiumViewSet, ConvertRuleViewSet, \
    ContainerViewSet, AssetBundleViewSet, ViewerJSViewSet, StatusViewSet, SpineViewSet

from .api.auth_views import login_view, discord_callback_view, discord_redirect_view, UserInfoViewSet

router = routers.DefaultRouter()
router.include_format_suffixes = False
router.register('game_version', GameVersionViewSet)
router.register('imperium', ImperiumViewSet)
router.register('convert_rule', ConvertRuleViewSet)
router.register('container', ContainerViewSet)
router.register('asset_bundle', AssetBundleViewSet)
router.register('viewer_js', ViewerJSViewSet)
router.register('status', StatusViewSet, basename='status')
router.register('user',UserInfoViewSet,basename='user')
router.register('spine',SpineViewSet,basename='spine')

schema_view = get_schema_view(title='Sdorica Inspector API')

urlpatterns = [

    path('schema/', schema_view),

    # http://localhost:8000/
    path('', index_view, name='index'),

    # http://localhost:8000/api/<router-viewsets>
    path('api/', include(router.urls)),

    # http://localhost:8000/api/admin/
    path('api/admin/', admin.site.urls),

    path('api-auth/', include('rest_framework.urls')),

    path('login', login_view),

    path('discord_oauth/redirect', discord_redirect_view),

    path('discord_oauth/callback', discord_callback_view)
]
