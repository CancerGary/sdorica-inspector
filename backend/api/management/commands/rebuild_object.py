import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.query_utils import Q

from backend.api.models import Imperium, UnityObject, Container, AssetBundle
from backend.api.tasks import _build_index_from_ab, _ab_task_db_index, _add_to_imperium_set
import time


class Command(BaseCommand):
    help = 'Delete all ab data index, and rebuild from imperiums (finished or celery_task_id)'

    def handle(self, *args, **options):

        print('Start rebuilding...')

        print('Delete all containers and objects first')
        c, _ = UnityObject.objects.all().delete()
        print('Delete %s UnityObject' % c)
        c, _ = Container.objects.all().delete()
        print('Delete %s Container' % c)
        c, _ = AssetBundle.objects.all().delete()
        print('Delete %s AssetBundle' % c)

        target_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle')
        ab_done = set()
        for i in Imperium.objects.filter(Q(finished=True) | Q(celery_task_id__isnull=False)):
            print('Current:', i.id, i.name, i.celery_task_id, i.finished)
            start_time = time.time()

            for ab_name, each_dict in i.load_data()['A'].items():
                md5, uid, url = each_dict['H'], each_dict['I'], each_dict['L']
                if md5 in ab_done:
                    continue
                print(_ab_task_db_index(ab_info=(md5, ab_name, url), target=target_dir))
                ab_done.add(md5)
            _add_to_imperium_set(None, imperium_id=i.id)

            print('Use:', time.time() - start_time)
