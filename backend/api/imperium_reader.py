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

def sort_table_keys(table:dict):
    keys_index_sorted = sorted(enumerate(table['K']), key=lambda x: x[1])
    index_sorted = [x[0] for x in keys_index_sorted]

    return {'K':[x[1] for x in keys_index_sorted],
            'D':[[x[i] for i in index_sorted] for x in table['D']],
            'T': [table['T'][i] for i in index_sorted]}

def c_diff(old_i, new_i):
    old:dict = old_i.get('C')
    new:dict = new_i.get('C')
    result = dict()
    if old and new:
        for new_table_title,new_table in new.items():
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
                    result[new_table_title]={'K': new_table['K'],
                                   'D': result_rows, 'T': new_table['T']}

            # old does't have, it's new
            else:
                result[new_table_title+' [+]'] = new_table

        # check old table deletion
        for old_table_title,old_table in old.items():
            if old_table_title not in new.keys():
                result[old_table+ ' [-]'] = old_table
        return {'C': result}
