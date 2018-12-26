import io
import pprint
import typing
import struct
import json
import collections

DEBUG_MODE=False

class ImperiumHandleError(Exception):
    def __init__(self,message):
        self.message=message

def handle_number(f, double_flag, base):
    i = f.read(1)
    if i[0] == double_flag:
        return struct.unpack('>H', f.read(2))[0]
    # elif i[0]==0xda:
    #     return handle_double(f)
    # elif 0xa0<=i[0]<0xc0:
    #     return i[0]-0xa0
    else:
        return i[0] - base  # guess


def handle_string(f):
    length = handle_number(f, 0xda, 0xa0)
    return f.read(length).decode('utf8')


def handle_type(f):
    tag=handle_string(f)
    if tag=='A':  # A
        result=dict()
        count = handle_number(f, 0xde, 0x80)
        for _ in range(count):
            # print(_)
            key = handle_string(f)
            l = []
            rows = handle_number(f, 0xde, 0x80)
            for _ in range(rows):
                i,j=handle_type(f)
                l.append(j)
            if DEBUG_MODE:
                print(key, l)
            result[key]=l
        return tag,dict(sorted(result.items()))
    elif tag in ['H','I','L']:  # H I L
        return tag,handle_string(f)
    elif tag in ['C']:  # C
        r_=[]
        count = handle_number(f, 0xde, 0x80)  # guess
        for _ in range(count):
            result = dict()
            title = handle_string(f)
            result['title']=title
            # c2=handle_number(f,)
            f.read(1)  # 0x83 ??
            result['keys'],result['rows']=handle_type(f)
            # change order of columns
            keys_index_sorted = sorted(enumerate(result['keys']), key=lambda x: x[1])
            result['keys'] = [x[1] for x in keys_index_sorted]
            index_sorted = [x[0] for x in keys_index_sorted]
            result['rows'] = [[x[i] for i in index_sorted] for x in result['rows']]
            if 'Key' in result['keys']:  # special handler for language data "Keys"
                result['rows'] = sorted(result['rows'],key=lambda x:x[result['keys'].index('Key')])
            r_.append(result)
        return tag,sorted(r_,key=lambda x:x['title'])
    elif tag in ['D']:  # D
        line_count = handle_number(f, 0xdc, 0x90)
        if DEBUG_MODE:
            print(line_count)
        if line_count == 0x10:  # ???
            return tag,None
        rows = []
        for _ in range(line_count):
            per_count = handle_number(f, 0xdc, 0x90)
            l = []
            for __ in range(per_count):
                k = f.read(1)[0]
                if k == 0xd2:
                    l.append(struct.unpack('>I', f.read(4))[0])
                elif k == 0xD1:
                    l.append(struct.unpack('>H', f.read(2))[0])
                else:
                    f.seek(f.tell() - 1)
                    l.append(handle_string(f))
                # print(l)
            if DEBUG_MODE:print(l)
            rows.append(l)

        k=handle_type(f)  # K # need add dict
        t=handle_type(f)  # T
        return k,rows
    elif tag in ['K','T']:  # K T
        count = handle_number(f, 0xdc, 0x90)
        if DEBUG_MODE:print(count)
        l = []
        for _ in range(count):
            l.append(handle_string(f))
        return l
    elif tag in ['E']:  # E
        if DEBUG_MODE:
            print(tag,'not implement')
        return tag,None
    elif tag in ['CT','PT']:
        k = f.read(1)[0]
        if k == 0xd2:
            return tag,struct.unpack('>I', f.read(4))[0]
        elif k == 0xD1:
            return tag,struct.unpack('>H', f.read(2))[0]
    elif tag in ['R']:
        k = f.read(1)[0]
        if k==0xcd:
            return tag,struct.unpack('>H', f.read(2))[0]
        else:
            return tag,k
    else:
        if DEBUG_MODE:
            print(f.tell(), tag)
        raise RuntimeError


def handle_file(f):
    try:
        i = f.read(1)
        result=dict()
        # print(i)
        for _ in range(i[0] - 0x80):
            if DEBUG_MODE:
                print(_)
            tag,data=handle_type(f)
            if data:
                result[tag]=data
        return dict(sorted(result.items()))
    except Exception as e:
        if __name__ == '__main__':
            raise e
        else:
            raise ImperiumHandleError(str(e))

def c_diff(old_i, new_i):
    old = old_i.get('C')
    new = new_i.get('C')
    result = []
    if old and new:
        for new_table in new:
            key_index = new_table['keys'].index('Key') if 'Key' in new_table['keys'] else -1
            old_table = [t for t in old if t['title'] == new_table['title']]
            # both have table, compare rows
            result_rows = []
            if old_table:
                old_table = old_table[0]
                # list -> tuple to make rows hashable
                old_rows = set([tuple(i) for i in old_table['rows']])
                new_rows = set([tuple(i) for i in new_table['rows']])

                for i in new_rows - old_rows:
                    i = list(i)
                    if key_index != -1: i[key_index] = i[key_index] + ' [+]'
                    result_rows.append(i)

                for i in old_rows - new_rows:
                    i = list(i)
                    if key_index != -1: i[key_index] = i[key_index] + ' [-]'
                    result_rows.append(i)

                if result_rows:
                    result_rows = sorted(result_rows, key=lambda x: x[key_index])
                    result.append({'title': new_table['title'], 'keys': new_table['keys'], 'rows': result_rows})

            # old does't have, it's new
            else:
                new_table['title'] = new_table['title'] + ' [+]'
                result.append(new_table)


        # check old table deletion
        for old_table in old:
            new_table = [t for t in old if t['title'] == old_table['title']]
            if not new_table:
                old_table['title'] = old_table + ' [-]'
                result.append(old_table)
        return {'C': result}

if __name__ == '__main__':
    json.dump(handle_file(open('localization_11_01', 'rb')),open('result','w'),indent=2)
