import requests
import hashlib
from backend.api.models import AssetBundle
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from backend.api.tasks import _ab_task_download


class Command(BaseCommand):
    help = 'Re-download all ab in database (useful when migrating the server)'

    def handle(self, *args, **options):
        print('Start re-download...')

        target_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle')
        os.makedirs(target_dir, exist_ok=True)
        for ab in AssetBundle.objects.all():
            print(_ab_task_download((ab.md5, '', ab.url), target_dir))

        print('Done!')
