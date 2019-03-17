import os
import hashlib

from celery import group, chord
from django.db import transaction
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

from .ab_utils import get_containers_from_ab, get_objects_from_ab
from .models import Imperium, AssetBundle, Container, UnityObject, UnityObjectRelationship
import unitypack
from .celery import app
from django.conf import settings
import requests
import traceback


@app.task
def ab_task(ab_info, target):
    return _ab_task(ab_info, target)


def _ab_task(ab_info, target):
    md5, uid, url = ab_info
    target_md5 = os.path.join(target, md5)
    if os.path.exists(target_md5):
        if hashlib.md5(open(target_md5, 'rb').read()).hexdigest() == md5:
            # print('pass:',md5,uid)
            return md5, url, target_md5

    # print('start:', md5, uid, url)
    retry = 5
    while True:
        try:
            c = requests.get(url, timeout=5).content
            open(target_md5, 'wb').write(c)
            break
        except requests.RequestException as e:
            if retry:
                retry -= 1
                # traceback.print_exc()
                continue
            else:
                raise e
    return md5, url, target_md5


@app.task
def build_index_and_done(finished_ab_info, imperium_id):
    return _build_index_and_done(finished_ab_info, imperium_id)


def _build_index_from_ab(ab, target_md5):
    # CAUTION: this function doesn't check if this ab has been indexed or not, so callers should check by themselves!
    # create containers
    # fetch first
    try:
        c = get_containers_from_ab(unitypack.load(open(target_md5, 'rb'))).keys()
    except Exception as e:
        logger.exception('get_containers_from_ab error')
        return
        # use set to sure each name add only once
    container_name_set = set(c)
    container_name_list = list(container_name_set)
    # print(len(container_name_set))

    # SQL may be too long, so make smaller sets to execute
    for first in range(0, len(container_name_list), 500):
        # calc containers not in database
        part = container_name_list[first:first + 500]
        part_exclude = set(part) - {i['name'] for i in Container.objects.filter(name__in=part).values('name')}
        # print('exclude:',container_name_exclude_set)
        # then create those not in database
        Container.objects.bulk_create([Container(name=n) for n in part_exclude])
        # query once to add the relations
        ab.container_set.add(*list(Container.objects.filter(name__in=part)))  # filter here

    # create unity objects
    # fetch first
    try:
        objects_list = get_objects_from_ab(unitypack.load(open(target_md5, 'rb')))
    except Exception as e:
        logger.exception('get_objects_from_ab error')
        return

    db_hash_set = {i[3] for i in objects_list}

    # create objects which don't exist
    db_hash_exclude = db_hash_set - {i['db_hash'] for i in
                                     UnityObject.objects.filter(db_hash__in=db_hash_set).values('db_hash')}
    unityobjects = []
    db_hash_used_set = set()  # even in a single file, there may be two objects have same db_hash!
    for name, path_id, data_hash, db_hash, asset_index, object_type in objects_list:
        if db_hash in db_hash_exclude and db_hash not in db_hash_used_set:
            unityobjects.append(UnityObject(name=name, data_hash=data_hash, db_hash=db_hash))
            db_hash_used_set.add(db_hash)
    bulk_result = UnityObject.objects.bulk_create(unityobjects)

    # add relations
    relationships = []
    db_hash_to_db_object = {uo.db_hash: uo for uo in UnityObject.objects.filter(db_hash__in=db_hash_set)}
    for name, path_id, data_hash, db_hash, asset_index, object_type in objects_list:
        relationships.append(
            UnityObjectRelationship(assetbundle=ab, unityobject=db_hash_to_db_object[db_hash],
                                    path_id=path_id, asset_index=asset_index))

    UnityObjectRelationship.objects.bulk_create(relationships)


def _build_index_and_done(finished_ab_info, imperium_id):
    # handle ab content centrally to reduce database IO times (bulk_create ?)
    # print(imperium_id)
    imperium = Imperium.objects.get(id=imperium_id)
    # add new assetbundles
    data = imperium.load_data()
    rev_dict = {w['H']: k for k, w in data['A'].items()}

    ab_objects = []

    with transaction.atomic():
        for md5, url, target_md5 in finished_ab_info:
            ab = AssetBundle(md5=md5, name=rev_dict[md5], url=url)
            ab.save()  # save to gain the PK
            _build_index_from_ab(ab, target_md5)

            # successfully analyzed
            ab_objects.append(ab)

    # add relations by group too
    imperium.assetbundle_set.add(*ab_objects)
    # mark finished
    imperium.finished = True
    imperium.save()


@app.task
def ab_list_task(imperium_id):
    imperium = Imperium.objects.get(id=imperium_id)
    data = imperium.load_data()
    if isinstance(data.get('A'), dict):
        target_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle')
        os.makedirs(target_dir, exist_ok=True)
        subtasks_info = []
        ab_objects = []
        for each_dict in data['A'].values():
            md5, uid, url = each_dict['H'], each_dict['I'], each_dict['L']
            target_md5 = os.path.join(target_dir, md5)
            if os.path.exists(target_md5) and hashlib.md5(open(target_md5, 'rb').read()).hexdigest() == md5:
                try:
                    ab = AssetBundle.objects.get(md5=md5)
                    ab_objects.append(ab)
                except AssetBundle.DoesNotExist:
                    subtasks_info.append((md5, uid, url))
            else:
                subtasks_info.append((md5, uid, url))
        # create not existed
        result = chord([ab_task.s(i, target_dir) for i in subtasks_info])(build_index_and_done.s(imperium_id))
        # add relation to existed
        imperium.assetbundle_set.add(*ab_objects)
        # print('group result',result.ready())
        return result
