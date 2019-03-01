import os
import msgpack

DEBUG_MODE = os.environ.get('IMPERIUM_DEBUG')


class ImperiumHandleError(Exception):
    def __init__(self, message):
        self.message = message


def handle_file(f):
    # You have reinvented the wheel again!
    try:
        return msgpack.load(f, encoding='utf8')
    except Exception as e:
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
                    result.append({'title': new_table['title'], 'keys': new_table['keys'],
                                   'rows': result_rows, 'type': new_table['type']})

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
