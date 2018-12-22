import io
import typing
import struct
import json
import collections

DEBUG_MODE=False
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

if __name__ == '__main__':
    json.dump(handle_file(open('localization_11_01', 'rb')),open('result','w'),indent=2)
