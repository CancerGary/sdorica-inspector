import os
import hashlib

from celery import group, chord

from .models import Imperium
from .celery import app
from django.conf import settings
import requests
import traceback

@app.task
def ab_task(ab_info: dict,target):
    md5, uid, url = ab_info
    target_md5 = os.path.join(target, md5)
    target_uid = os.path.join(target, uid)
    if os.path.exists(target_uid):
        if hashlib.md5(open(target_uid, 'rb').read()).hexdigest() == md5:
            if os.path.exists(target_md5):
                os.remove(target_uid)
            else:
                os.rename(target_uid, target_md5)
            return
    elif os.path.exists(target_md5):
        if hashlib.md5(open(target_md5, 'rb').read()).hexdigest() == md5:
            # print('pass:',md5,uid)
            return

    print('start:', md5, uid, url)
    while True:
        try:
            c = requests.get(url, timeout=5).content
            open(target_md5, 'wb').write(c)
            break
        except requests.RequestException:
            traceback.print_exc()
            continue
@app.task
def mark_done(_,imperium_id):
    print(imperium_id)
    i = Imperium.objects.get(id=imperium_id)
    i.finished = True
    i.save()

@app.task
def ab_list_task(imperium_id):
    data = Imperium.objects.get(id=imperium_id).load_data()
    if isinstance(data.get('A'), dict):
        target = os.path.join(settings.INSPECTOR_DATA_ROOT, 'assetbundle')
        result = chord([ab_task.s(i,target) for i in list(data['A'].values())])(mark_done.s(imperium_id))
        # print('group result',result.ready())
        return result