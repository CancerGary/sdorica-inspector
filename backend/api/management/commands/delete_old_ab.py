import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.query_utils import Q
from django.utils import timezone

from backend.api.models import Imperium, UnityObject, Container, AssetBundle
from backend.api.tasks import _build_index_from_ab, _ab_task_db_index, _add_to_imperium_set
import time


class Command(BaseCommand):
    help = 'Delete the ABs of the old imperium'

    def add_arguments(self, parser):
        parser.add_argument('number', nargs='+', type=int)

    def handle(self, *args, **options):
        imperium_list = Imperium.objects.filter(
            create_time__gt=timezone.datetime(options['number'][0], options['number'][1], options['number'][2]),
            finished=True)

        print(imperium_list)
        if input("Will **only keep** these imperiums? (yes)") == 'yes':
            keep_set = set()
            for i in imperium_list:
                keep_set |= {m[0] for m in i.assetbundle_set.values_list('md5')}
            print("Keep these:")
            print(keep_set)
            if input("[%d] Ready? (yes)" % len(keep_set)) != 'yes': return
            base_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle')
            i = 0
            for filename in os.listdir(base_dir):
                if filename not in keep_set:
                    try:
                        os.remove(os.path.join(base_dir, filename))
                        i += 1
                    except FileNotFoundError:
                        continue
            print("%d files have been deleted" % i)
