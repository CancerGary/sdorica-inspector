import base64
from collections import OrderedDict

import fsb5
from unitypack.assetbundle import AssetBundle as upAssetBundle
from unitypack.object import ObjectPointer


def get_containers_from_ab(bundle: upAssetBundle) -> dict:
    result = dict()
    for asset in bundle.assets:
        # print("%s: %s:: %i objects" % (bundle, asset, len(asset.objects)))
        try:
            # asset.objects may raise exception
            if len(asset.objects) == 0: continue
        except:
            continue
        # for id, object in asset.objects.items():
        #     print(id, object.read())
        # print(asset.objects.keys())
        if asset.objects.get(1):
            c_desc = asset.objects.get(1).read().get('m_Container')
            if c_desc:
                # get container name only
                result.update({i[0]: i[1] for i in c_desc})
    return result

def strip_pointers(object):
    if type(object) in [OrderedDict,dict]:
        return {k:strip_pointers(v) for k,v in object.items()}
    elif type(object) in [list]:
        return [strip_pointers(i) for i in object]
    elif type(object) is ObjectPointer:
        return object.path_id
    elif type(object) is bytes:
        return base64.b64encode(object)
    else:
        try:
            return strip_pointers(object._obj)
        except AttributeError:
            return object

def handle_fsb(data):
    fsb = fsb5.load(data)
    for sample in fsb.samples:
        # assume 1 sample
        return fsb.rebuild_sample(sample).tobytes()