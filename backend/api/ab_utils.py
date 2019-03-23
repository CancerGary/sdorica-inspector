import base64
import hashlib
from collections import OrderedDict

import fsb5
from unitypack.assetbundle import AssetBundle as upAssetBundle
from unitypack.object import ObjectPointer
import zlib

RECORD_UNITY_TYPES = ['Texture2D', 'TextAsset']

md5 = lambda x:hashlib.md5(x).hexdigest()
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
        if asset.objects.get(1) and asset.objects.get(1).type == 'AssetBundle':
            c_desc = asset.objects.get(1).read().get('m_Container')
            if c_desc:
                # get container name only
                result.update({i[0]: i[1] for i in c_desc})
    return result


def get_objects_from_ab(bundle: upAssetBundle) -> list:
    '''
    Get objects info form an asset bundle
    There are some objects having same name, so the function return a list of tuples
    :param bundle: an AssetBundle
    :return: objects list contains (name, path_id, data_hash, db_hash, asset_index, object_type)
    '''
    result = list()
    for asset in bundle.assets:
        index = bundle.assets.index(asset)
        try:
            # asset.objects may raise exception
            if len(asset.objects) == 0: continue
        except:
            continue
        for path_id, object in asset.objects.items():
            if object.type not in RECORD_UNITY_TYPES:
                continue
            data_hash = None
            data = object.read()
            # extend types here
            if object.type == 'Texture2D':
                if getattr(data, 'image_data'):
                    data_hash = md5(data.image_data)
            elif object.type == 'TextAsset':
                if getattr(data, 'bytes'):
                    # WTF ??
                    data_hash = md5(data.bytes.encode() if isinstance(data.bytes, str) else data.bytes)
            else:
                continue

            if data_hash:
                # db_hash <- crc32(name+data_hash)
                result.append((data.name, path_id, data_hash,
                               md5((data.name + str(data_hash)).encode()), index, object.type))
    return result


def strip_pointers(object):
    if type(object) in [OrderedDict, dict]:
        return {k: strip_pointers(v) for k, v in object.items()}
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

def split_path_id(path_id):
    if isinstance(path_id, str) and ':' in path_id:
        return int(path_id.split(':')[-2]), int(path_id.split(':')[-1])
    else:
        return None, int(path_id)