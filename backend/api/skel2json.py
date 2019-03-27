import json
import struct
from io import BytesIO
from typing import BinaryIO
import pprint
import ctypes


def int_overflow(val):
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def unsigned_right_shitf(n, i):
    if n < 0:
        n = ctypes.c_uint32(n).value
    if i < 0:
        return -int_overflow(n << abs(i))
    # print(n)
    return int_overflow(n >> i)


BLEND_MODE = ['normal', 'additive', 'multiply', 'screen']
ATTACHMENT_TYPE = ['region', 'boundingbox', 'mesh', 'weightedmesh', 'linkedmesh', 'weightedlinkedmesh']

TIMELINE_TYPE = ['rotate', 'translate', 'scale', 'shear', 'attachment', 'color']

CURVE_TYPE = ['linear', 'stepped', 'bezier']


class Handler():
    def __init__(self, f: BinaryIO, for_new=True):
        self.f = f
        self.nonessential = False
        self._result = dict()
        self._skin_index = list()
        self.for_new = for_new

    def read(self, l=1):
        b = self.f.read(l)
        return b[0] if l == 1 else b

    def read_var_int(this, optimizePositive):
        b = this.read()
        result = b & 127
        if ((b & 128) != 0):
            b = this.read()
            result |= (b & 127) << 7
            if ((b & 128) != 0):
                b = this.read()
                result |= (b & 127) << 14
                if ((b & 128) != 0):
                    b = this.read()
                    result |= (b & 127) << 21
                    if ((b & 128) != 0):
                        b = this.read()
                        result |= (b & 127) << 28
        # return optimizePositive ? result : result >>> 1 ^ -(result & 1);
        # return result if optimizePositive else ((-1 & (2**32-1)) >> 1) ^ -(result & 1)
        return int_overflow(result) if optimizePositive else unsigned_right_shitf(result, 1) ^ -(result & 1)

    def read_string(self):
        char_count = self.read_var_int(True)
        if char_count == 0: return None
        if char_count == 1: return ''
        if char_count == 2: return chr(self.read())
        return self.read(char_count - 1).decode('utf8')  # readUtf8_slow

    def handle_skeleton(self):
        result = {'hash': self.read_string(),
                  'spine': self.read_string(),
                  'width': self.read_float(),
                  'height': self.read_float()}
        self.nonessential = self.read_bool()
        # print(self.nonessential)
        result['images'] = self.read_string() if self.nonessential else None
        return result

    def handle_bones(self):
        result = []
        bones_count = self.read_var_int(True)
        # print(bones_count)
        for i in range(bones_count):
            # print(i, '/', bones_count)
            r = {
                'name': self.read_string(),
                'parent': result[self.read_var_int(True)]['name'] if i != 0 else None,
                'rotation': self.read_float(),
                'x': self.read_float(),
                'y': self.read_float(),
                'scaleX': self.read_float(),
                'scaleY': self.read_float(),
                'shearX': self.read_float(),
                'shearY': self.read_float(),
                'length': self.read_float(),
                'inheritRotation': self.read_bool(),
                'inheritScale': self.read_bool(),
            }
            if self.nonessential: r['color'] = self.read_rgba8888()
            if self.for_new:
                # transform: Determines how parent bone transforms are inherited:
                # normal, onlyTranslation, noRotationOrReflection, noScale, or noScaleOrReflection.
                # Assume normal if omitted.
                # print((r['name'], r['inheritRotation'], r['inheritScale']))
                r['transform'] = {(True, True): 'normal',
                                  (True, False): 'noScale',
                                  (False, True): 'noRotationOrReflection',
                                  (False, False): 'onlyTranslation'}.get((r['inheritRotation'], r['inheritScale']),
                                                                         'normal')
            result.append(r)
        return result

    def rvit(self):
        return self.read_var_int(True)

    def get_bone_name(self, index):
        return self._result['bones'][index]['name']

    def get_slot_name(self, index):
        return self._result['slots'][index]['name']

    def handle_ik(self):
        result = []
        for i in range(self.rvit()):
            result.append({
                'name': self.read_string(),
                'bones': [self.get_bone_name(self.rvit()) for i in range(self.rvit())],
                'target': self.get_bone_name(self.rvit()),
                'mix': self.read_float(),
                'bendPositive': (self.read_byte() == 1),
                # for_new: Constraint order can be specified after `3.5.00-beta`
                # The default value is `0`, which means if the value is lost, only first IK Constraint will work.
                'order': i  # data.order = this.getValue(constraintMap, "order", 0);
            })
        return result

    def handle_transform(self):
        result = []
        for i in range(self.rvit()):
            d = {
                'name': self.read_string(),
                'bone': self.get_bone_name(self.rvit()),
                'target': self.get_bone_name(self.rvit()),
                'rotation': self.read_float(),
                'x': self.read_float(),
                'y': self.read_float(),
                'scaleX': self.read_float(),
                'scaleY': self.read_float(),
                'shearY': self.read_float(),
                'rotateMix': self.read_float(),
                'translateMix': self.read_float(),
                'scaleMix': self.read_float(),
                'shearMix': self.read_float(),
                'order': i  # same to ik order
            }
            # for (JsonValue boneMap = constraintMap.getChild("bones"); boneMap != null; boneMap = boneMap.next) {
            if self.for_new:
                d['bones'] = [d.pop('bone')]
            result.append(d)
        return result

    def handle_slots(self):
        result = []
        slots_count = self.rvit()
        # print(slots_count)
        for i in range(slots_count):
            # print(i)
            d = {
                'name': self.read_string(),
                'bone': self.get_bone_name(self.rvit()),
                'color': self.read_rgba8888(), }
            a = self.read_string()
            if a: d.update({'attachment': a})
            d.update({
                'blend': BLEND_MODE[self.rvit()]
            })
            result.append(d)
        return result

    def read_float_array(self, length):
        return [self.read_float() for i in range(length)]

    def read_short(self):
        return struct.unpack('>h', self.read(2))[0]

    def read_short_array(self):
        return [self.read_short() for i in range(self.rvit())]

    def read_skin(self):
        slot_count = self.rvit()
        if slot_count == 0: return None
        skin_result = dict()  # ['slotName']
        for i in range(slot_count):
            slot_result = dict()  # ['attachmentName']
            slot_index = self.rvit()
            for ii in range(self.rvit()):  # attachment count
                placeholder_name = self.read_string()
                name = self.read_string()
                if not name: name = placeholder_name
                type = ATTACHMENT_TYPE[self.read()]
                d = {
                    'name': name,
                    'type': type
                }
                if type == 'region':
                    d.update({
                        'path': self.read_string(),
                        'rotation': self.read_float(),
                        'x': self.read_float(),
                        'y': self.read_float(),
                        'scaleX': self.read_float(),
                        'scaleY': self.read_float(),
                        'width': self.read_float(),
                        'height': self.read_float(),
                        'color': self.read_rgba8888(),  # ?
                    })
                elif type == 'boundingbox':
                    d.update({
                        'vertices': self.read_float_array(self.rvit() * 2),
                        # 'color': self.read_rgba8888(),
                    })
                elif type == 'mesh':
                    d.update({
                        'path': self.read_string(),
                        'color': self.read_rgba8888(), })
                    vertices_length = self.rvit() * 2
                    d.update({
                        'uvs': self.read_float_array(vertices_length),
                        'triangles': self.read_short_array(),
                        'vertices': self.read_float_array(vertices_length),
                        'hull': self.rvit()})

                    if self.nonessential:
                        d.update({
                            'edges': self.read_short_array(),
                            'width': self.read_float(),
                            'height': self.read_float(),
                        })
                elif type in ['linkedmesh', 'weightedlinkedmesh']:
                    # print(type)
                    if type == 'weightedlinkedmesh' and self.for_new:
                        d.update({'type': 'linkedmesh'})
                    d.update({
                        'path': self.read_string(),
                        'color': self.read_rgba8888(),
                        'skin': self.read_string(),
                        'parent': self.read_string(),
                        'deform': self.read_bool(),  # inheritFFD
                    })
                    if self.nonessential:
                        d.update({
                            'width': self.read_float(),
                            'height': self.read_float()
                        })
                elif type == 'weightedmesh':
                    if type == 'weightedmesh' and self.for_new:
                        d.update({'type': 'mesh'})
                    d.update({
                        'path': self.read_string(),
                        'color': self.read_rgba8888(), })
                    vertex_count = self.rvit()
                    d.update({
                        'uvs': self.read_float_array(vertex_count * 2),
                        'triangles': self.read_short_array(), })
                    # complex here
                    # vertices = [(bone_count,(float*4)*bone_count))*vertex_count]
                    vertices = []
                    for i in range(vertex_count):
                        bone_count = self.read_float()
                        vertices.append(bone_count)
                        for ii in range(int(bone_count)):
                            vertices += self.read_float_array(4)

                    d.update({'vertices': vertices,
                              'hull': self.rvit()
                              })
                    if self.nonessential:
                        d.update({
                            'edges': self.read_short_array(),
                            'width': self.read_float(),
                            'height': self.read_float(),
                        })
                # js null
                if d.get('path') is None:
                    # print('get: ',d['path'])
                    d.pop('path')

                slot_result[placeholder_name] = d
            skin_result[self.get_slot_name(slot_index)] = slot_result
        return skin_result

    def handle_skins(self):
        result = dict()
        result['default'] = self.read_skin()
        self._skin_index.append('default')
        for i in range(self.rvit()):
            skin_name = self.read_string()
            self._skin_index.append(skin_name)
            result[skin_name] = self.read_skin()
        return result

    def handle_events(self):
        result = []
        for i in range(self.rvit()):
            result.append({
                'name': self.read_string(),
                'int': self.read_var_int(False),
                'float': self.read_float(),
                'string': self.read_string()
            })
        return result

    def handle_animations(self):
        result = dict()
        for i in range(self.rvit()):
            name = self.read_string()
            animation = {
                'slots': dict(),
                'bones': dict(),
                'ik': dict(),
                'transform': dict(),
                'ffd': dict(),
                # 'draworder': dict(),
                # 'events': dict(),
            }
            # readAnimation

            # slot timelines
            for i in range(self.rvit()):
                slot_index = self.rvit()
                slot_name = self.get_slot_name(slot_index)
                animation['slots'][slot_name] = dict()
                for ii in range(self.rvit()):
                    timeline_type = TIMELINE_TYPE[self.read()]
                    frame_count = self.rvit()
                    timeline_data = []
                    if timeline_type == 'color':
                        for fi in range(frame_count):
                            d = {
                                'time': self.read_float(),
                                'color': self.read_rgba8888(),
                            }
                            if fi < frame_count - 1:
                                d.update({'curve': self.read_curve()})

                            timeline_data.append(d)
                    elif timeline_type == 'attachment':
                        for fi in range(frame_count):
                            d = {
                                'time': self.read_float(),
                                'name': self.read_string()
                            }
                            timeline_data.append(d)
                    else:
                        raise NotImplementedError
                    animation['slots'][slot_name][timeline_type] = timeline_data

            # bone timelines
            for i in range(self.rvit()):
                bone_index = self.rvit()
                bone_name = self.get_bone_name(bone_index)
                animation['bones'][bone_name] = dict()
                for ii in range(self.rvit()):
                    timeline_type = TIMELINE_TYPE[self.read()]
                    frame_count = self.rvit()
                    timeline_data = []
                    if timeline_type == 'rotate':
                        for fi in range(frame_count):
                            d = {
                                'time': self.read_float(),
                                'angle': self.read_float()
                            }
                            if fi < frame_count - 1:
                                d.update({'curve': self.read_curve()})
                            timeline_data.append(d)
                    elif timeline_type in ['translate', 'scale', 'shear']:
                        for fi in range(frame_count):
                            d = {
                                'time': self.read_float(),
                                'x': self.read_float(),
                                'y': self.read_float()
                            }
                            if fi < frame_count - 1:
                                d.update({'curve': self.read_curve()})
                            timeline_data.append(d)
                    else:
                        raise NotImplementedError
                    animation['bones'][bone_name][timeline_type] = timeline_data

            # ik timelines
            for i in range(self.rvit()):
                ik_index = self.rvit()
                ik_constraint_name = self._result['ik'][ik_index]['name']
                frame_count = self.rvit()
                timeline_data = []
                for fi in range(frame_count):
                    d = {
                        'time': self.read_float(),
                        'mix': self.read_float(),
                        'bendPositive': (self.read_byte() == 1)
                    }
                    if fi < frame_count - 1:
                        d.update({'curve': self.read_curve()})
                    timeline_data.append(d)
                animation['ik'][ik_constraint_name] = timeline_data

            # transform
            for i in range(self.rvit()):
                transform_index = self.rvit()
                transform_constraint_name = self._result['transform'][transform_index]['name']
                frame_count = self.rvit()
                timeline_data = []
                for fi in range(frame_count):
                    d = {
                        'time': self.read_float(),
                        'rotateMix': self.read_float(),
                        'translateMix': self.read_float(),
                        'scaleMix': self.read_float(),
                        'shearMix': self.read_float()
                    }
                    if fi < frame_count - 1:
                        d.update({'curve': self.read_curve()})
                    timeline_data.append(d)
                animation['transform'][transform_constraint_name] = timeline_data

            # FFD
            for i in range(self.rvit()):
                skin_index = self.rvit()
                skin_name = self._skin_index[skin_index]
                skin_data = dict()
                for ii in range(self.rvit()):
                    slot_index = self.rvit()
                    slot_name = self.get_slot_name(slot_index)
                    slot_data = dict()
                    for iii in range(self.rvit()):
                        attachment_name = self.read_string()
                        frame_count = self.rvit()
                        timeline_data = []

                        for fi in range(frame_count):
                            d = {
                                'time': self.read_float()
                            }

                            v_end = self.rvit()

                            if v_end != 0:
                                vertices = []
                                v_start = self.rvit()
                                # Java
                                # end += start;
                                # for (int v = start; v < end; v++) // len = end
                                for _ in range(v_end):
                                    vertices.append(self.read_float())
                                d.update({
                                    'offset': v_start,
                                    'vertices': vertices
                                })

                            if fi < frame_count - 1:
                                d.update({'curve': self.read_curve()})
                            timeline_data.append(d)
                        slot_data[attachment_name] = timeline_data
                    skin_data[slot_name] = slot_data
                animation['ffd'][skin_name] = skin_data

            # draworder
            draworder = []
            for i in range(self.rvit()):
                d = {
                    'time': self.read_float(),
                }
                offset_count = self.rvit()
                offsets = []
                for ii in range(offset_count):
                    offsets.append({
                        'slot': self.get_slot_name(self.rvit()),
                        'offset': self.rvit()
                    })
                d.update({
                    'offsets': offsets
                })
                draworder.append(d)
            if draworder: animation['draworder'] = draworder

            # event
            events = []
            for i in range(self.rvit()):
                d = {
                    'time': self.read_float(), }
                event_index = self.rvit()  # eventData
                d.update({
                    'int': self.read_var_int(False),
                    'name': self._result['events'][event_index]['name'],
                    'float': self.read_float(),
                    'string': self.read_string() if self.read_bool()
                    else self._result['events'][event_index]['string']
                })
                events.append(d)
            if events:  # readAnimation error
                animation['events'] = events

            # check new (ffd->deform)
            if self.for_new:
                animation['deform'] = animation.pop('ffd')

            # add single animation data
            result[name] = animation
            # print(animation)

        return result

    def read_curve(self):
        curve_type = CURVE_TYPE[self.read()]
        if curve_type == 'stepped':
            return 'stepped'
        elif curve_type == 'bezier':
            return [self.read_float() for i in range(4)]

    def handle(self):
        self.f.seek(0)
        self._result = dict()
        self._result['skeleton'] = self.handle_skeleton()
        self._result['bones'] = self.handle_bones()
        self._result['ik'] = self.handle_ik()
        self._result['transform'] = self.handle_transform()
        self._result['slots'] = self.handle_slots()
        self._result['skins'] = self.handle_skins()
        self._result['events'] = self.handle_events()
        self._result['animations'] = self.handle_animations()
        return self._result

    def read_float(self):
        return struct.unpack('>f', self.read(4))[0]

    def read_bool(self):
        return self.read() != 0

    def read_byte(self):
        b = self.read()
        # print(b)
        return b - 256 if b > 127 else b

    def read_rgba8888(self):
        b = self.read(4)
        return '#%02x%02x%02x%02x' % (b[0], b[1], b[2], b[3])


if __name__ == '__main__':
    result = Handler(open('data.skel', 'rb')).handle()
    # pprint.pprint(result)
    json.dump(result, open('data.json', 'w'))
