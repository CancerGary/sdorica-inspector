import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from backend.api.models import Imperium, UnityObject, Container, AssetBundle
from backend.api.tasks import _build_index_from_ab
import time


class Command(BaseCommand):
    help = 'Delete all containers and objects, then rebuild from ab.'

    def handle(self, *args, **options):

        print('Start rebuilding...')

        print('Delete all containers and objects first')
        c, _ = UnityObject.objects.all().delete()
        print('Delete %s UnityObject' % c)
        c, _ = Container.objects.all().delete()
        print('Delete %s Container' % c)

        target_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle')
        ab_done = set()
        for i in Imperium.objects.filter(finished=True):
            print('Current:', i.id, i.name)
            start_time = time.time()
            for ab in i.assetbundle_set.all():
                if ab.md5 not in ab_done:
                    _build_index_from_ab(ab, os.path.join(target_dir, ab.md5))
                ab_done.add(ab.md5)
            print('Use:', time.time() - start_time)
