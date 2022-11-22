from backend.api.models import *
from backend.api.tasks import _build_index_from_ab, _ab_task_db_index, _add_to_imperium_set
imperiums = Imperium.objects.filter(create_time__gt="2022-09-13").all()
ab_done = set()
target_dir = os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle')
AB_NAME_SKIP = ["scene.ab"]
for i in imperiums:
    print(i.name,i.md5)
    data = i.load_data()
    if isinstance(data.get('A'), dict):
        print('Current:', i.id, i.name, i.celery_task_id, i.finished)
        start_time = time.time()
        for ab_name, each_dict in i.load_data()['A'].items():
            if ab_name in AB_NAME_SKIP:
                continue
            md5, uid, url = each_dict['H'], each_dict['I'], each_dict['L']
            if md5 in ab_done:
                continue
            print(md5, uid, url)
            AssetBundle.objects.filter(md5=md5).delete()
            print(_ab_task_db_index(ab_info=(md5, ab_name, url), target=target_dir))
            ab_done.add(md5)
        print('_add_to_imperium_set', i.id)
        _add_to_imperium_set(None, imperium_id=i.id)
        print('Use:', time.time() - start_time)


i = Imperium.objects.get(name='android 22-10-12')
for ab_name, each_dict in i.load_data()['A'].items():
    md5, uid, url = each_dict['H'], each_dict['I'], each_dict['L']
    if md5 =='81763ce535c72829aa6fd3978761fe2d':
        print(md5,uid,url)
        break