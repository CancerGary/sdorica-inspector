import difflib
import os
import msgpack

DEBUG_MODE = os.environ.get('IMPERIUM_DEBUG')


class ImperiumHandleError(Exception):
    def __init__(self, message):
        self.message = message


def handle_file(f):
    # You have reinvented the wheel again!
    try:
        j = msgpack.load(f, encoding='utf8')
        if j.get('C'):
            j['C'] = {k: sort_table_keys(j['C'][k]) for k in sorted(j['C'])}
        return j
    except Exception as e:
        raise ImperiumHandleError(str(e))


def sort_table_keys(table: dict):
    keys_index_sorted = sorted(enumerate(table['K']), key=lambda x: x[1])
    index_sorted = [x[0] for x in keys_index_sorted]

    return {'K': [x[1] for x in keys_index_sorted],
            'D': [[x[i] for i in index_sorted] for x in table['D']],
            'T': [table['T'][i] for i in index_sorted]}


def c_diff(old_i, new_i):
    old: dict = old_i.get('C')
    new: dict = new_i.get('C')
    result = dict()
    if old and new:
        for new_table_title, new_table in new.items():
            new_table = sort_table_keys(new_table)
            key_index = new_table['K'].index('Key') if 'Key' in new_table['K'] else -1
            # both have table, compare rows
            result_rows = []
            if new_table_title in old.keys():
                old_table = sort_table_keys(old[new_table_title])
                # list -> tuple to make rows hashable
                old_rows = set([tuple(i) for i in old_table['D']])
                new_rows = set([tuple(i) for i in new_table['D']])

                for i in new_rows - old_rows:
                    i = list(i)
                    if key_index != -1: i[key_index] = i[key_index] + ' [+]'
                    result_rows.append(i)

                for i in old_rows - new_rows:
                    i = list(i)
                    if key_index != -1: i[key_index] = i[key_index] + ' [-]'
                    result_rows.append(i)

                if result_rows:
                    # result_rows = sorted(result_rows, key=lambda x: x[key_index])
                    result[new_table_title] = {'K': new_table['K'],
                                               'D': result_rows, 'T': new_table['T']}

            # old does't have, it's new
            else:
                result[new_table_title + ' [+]'] = new_table

        # check old table deletion
        for old_table_title, old_table in old.items():
            if old_table_title not in new.keys():
                result[old_table_title + ' [-]'] = old_table
        return {'C': result}


def c_to_text(c: dict, e: dict, title_subfix="", show_type=False, show_index=True, str_func=repr, cell_cep=', '):
    def generate_row_string(row: list):
        return cell_cep.join(
            map(lambda i: "%s$%d" % (str_func(i[1]), i[0]), enumerate(row)) if show_index else map(str_func, row))

    result = ""
    for title in sorted(c.keys()):
        content = sort_table_keys(c[title])
        if show_type:
            key_row = generate_row_string(["%s[%s]" % (x, y) for x, y in zip(content['K'], content['T'])])
        else:
            key_row = generate_row_string(["%s" % (x) for x in content['K']])
        # replace original enum to string
        content['D'] = [
            [e[t][d] if t.startswith('enum') and e.get(t) and d < len(e[t]) else d for d, t in zip(row, content['T'])]
            for row in content['D']
        ]

        # two new lines to make the result doesn't compare between header and row
        result += "%s%s\n%s%s\n\n%s\n\n" % (title, title_subfix,
                                            key_row,
                                            title_subfix,
                                            "\n".join(map(lambda m: generate_row_string(m), content['D'])))
    return result


def c_diff_text(old_i, new_i, show_type, show_index, str_func=repr, cell_cep=', ', n=0):
    old: dict = old_i.get('C')
    new: dict = new_i.get('C')
    # remove no change table to make the result more concise
    for k in list(old.keys()):
        if old.get(k) == new.get(k):
            old.pop(k)
            new.pop(k)
    return "\n".join(
        difflib.unified_diff(
            c_to_text(old, old_i.get('E'), show_type=show_type, show_index=show_index, str_func=str_func,
                      cell_cep=cell_cep).splitlines(),
            c_to_text(new, new_i.get('E'), show_type=show_type, show_index=show_index, str_func=str_func,
                      cell_cep=cell_cep, title_subfix='$').splitlines(),
            lineterm="", fromfile='left', tofile='right', n=n))
