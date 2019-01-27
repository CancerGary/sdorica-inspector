import os
import hashlib

from celery import group, chord

from .models import Imperium, AssetBundle, Container
import unitypack
from unitypack.assetbundle import AssetBundle as upAssetBundle
from .celery import app
from django.conf import settings
import requests
import traceback


def get_containers_from_ab(bundle: upAssetBundle) -> list:
    result = []
    for asset in bundle.assets:
        # print("%s: %s:: %i objects" % (bundle, asset, len(asset.objects)))
        if len(asset.objects) == 0: continue
        # for id, object in asset.objects.items():
        #     print(id, object.read())
        # print(asset.objects.keys())
        if asset.objects.get(1):
            c_desc = asset.objects.get(1).read().get('m_Container')
            if c_desc:
                # get container name only
                result += [i[0] for i in c_desc]
    return result


@app.task
def ab_task(ab_info: dict, target):
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
                traceback.print_exc()
                continue
            else:
                raise e
    return md5, url, target_md5


@app.task
def build_index_and_done(finished_ab_info, imperium_id):
    # handle ab content centrally to reduce database IO times (bulk_create ?)
    # print(imperium_id)
    imperium = Imperium.objects.get(id=imperium_id)
    # add new assetbundles
    data = imperium.load_data()
    rev_dict = {w[0]: k for k, w in data['A'].items()}

    for md5, url, target_md5 in finished_ab_info:
        ab = AssetBundle(md5=md5, name=rev_dict[md5], url=url)
        ab.save()
        ab.imperiums.add(imperium)
        # create containers
        try:
            for container_name in get_containers_from_ab(unitypack.load(open(target_md5,'rb'))):
                try:
                    # TODO:optimize container creating
                    container = Container.objects.get(name=container_name)
                except Container.DoesNotExist:
                    container = Container(name=container_name)
                    container.save()
                container.asset_bundles.add(ab)
        except:
            traceback.print_exc()
            continue

    imperium.finished = True
    imperium.save()


@app.task
def ab_list_task(imperium_id):
    imperium = Imperium.objects.get(id=imperium_id)
    data = imperium.load_data()
    if isinstance(data.get('A'), dict):
        target_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle')
        subtasks_info = []
        for md5, uid, url in data['A'].values():
            target_md5 = os.path.join(target_dir, md5)
            if os.path.exists(target_md5) and hashlib.md5(open(target_md5, 'rb').read()).hexdigest() == md5:
                try:
                    ab = AssetBundle.objects.get(md5=md5)
                    ab.imperiums.add(imperium)
                except AssetBundle.DoesNotExist:
                    subtasks_info.append((md5, uid, url))
            else:
                subtasks_info.append((md5, uid, url))

        result = chord([ab_task.s(i, target_dir) for i in subtasks_info])(build_index_and_done.s(imperium_id))
        # print('group result',result.ready())
        return result
