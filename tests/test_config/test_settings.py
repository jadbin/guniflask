from guniflask.config import Settings


def test_get():
    d = {'key': 'value'}
    c = Settings(d)
    assert len(c) == 1
    for k in c:
        assert k == 'key' and c[k] == 'value'
    assert c.get('key') == 'value'
    assert c.get('no_such_key') is None
    assert c.get('no_such_key', 'default') == 'default'
    assert c.get('key', 'default') == 'value'
    assert c['key'] == 'value'
    assert c['no_such_key'] is None
    assert ('key' in c) is True
    assert ('no_such_key' in c) is False


def test_get_bool():
    d = {'bool_true': 'true', 'bool_True': 'True', 'bool_false': 'false', 'bool_False': 'False',
         'bool_int1': '1', 'bool_int0': '0', 'bool_none': '...',
         'true': True, 'false': False}
    c = Settings(d)
    assert c.getbool('true') is True
    assert c.getbool('false') is False
    assert c.getbool('bool_true') is True
    assert c.getbool('bool_True') is True
    assert c.getbool('bool_false') is False
    assert c.getbool('bool_False') is False
    assert c.getbool('bool_int1') is True
    assert c.getbool('bool_int0') is False
    assert c.getbool('bool_none') is None
    assert c.getbool('bool_no') is None
    assert c.getbool('bool_no', True) is True
    assert c.getbool('bool_no', False) is False
    assert c.getbool('bool_no', '...') is None
    assert c.getbool('bool_true', False) is True
    assert c.getbool('bool_false', True) is False


def test_get_int():
    d = {'int_1': 1, 'int_str_1': '1', 'int_none': '...'}
    c = Settings(d)
    assert c.getint('int_1') == 1
    assert c.getint('int_str_1') == 1
    assert c.getint('int_none') is None
    assert c.getint('int_no') is None
    assert c.getint('int_1', 0) == 1
    assert c.getint('int_none', 0) is None
    assert c.getint('int_no', 0) == 0


def test_get_float():
    d = {'float_1.1': 1.1, 'float_str_1.1': '1.1', 'float_none': '...'}
    c = Settings(d)
    assert c.getfloat('float_1.1') == 1.1
    assert c.getfloat('float_str_1.1') == 1.1
    assert c.getfloat('float_none') is None
    assert c.getfloat('float_no') is None
    assert c.getfloat('float_1.1', 0) == 1.1
    assert c.getfloat('float_none', 0) is None
    assert c.getfloat('float_no', 0) == 0


def test_get_list():
    d = {'list': [1, 2], 'tuple': (1, 2), 'single': 1, 'list_str': '1,2'}
    c = Settings(d)
    assert c.getlist('list') == [1, 2]
    assert c.getlist('tuple') == [1, 2]
    assert c.getlist('single') == [1]
    assert c.getlist('list_str') == ['1', '2']
    assert c.getlist('list', [1]) == [1, 2]
    assert c.getlist('no_such_list') is None
    assert c.getlist('no_such_list', [1]) == [1]


def test_set():
    c = Settings()
    c.set('key', 'value')
    assert len(c) == 1 and c['key'] == 'value'

    c.set('key', 'value2')
    assert c['key'] == 'value2'

    c.set('key2', 'value')
    assert len(c) == 2 and c['key2'] == 'value'


def test_set_item():
    c = Settings()
    c['key'] = 'value'
    assert len(c) == 1 and c['key'] == 'value'

    c['key'] = 'value2'
    assert c['key'] == 'value2'

    c['key2'] = 'value'
    assert len(c) == 2 and c['key2'] == 'value'


def test_update():
    c = Settings()
    c.update({'key': 'value'})
    assert len(c) == 1 and c['key'] == 'value'

    c.update({'key': 'value2', 'key2': 'value'})
    assert len(c) == 2 and c['key'] == 'value2' and c['key2'] == 'value'


def test_update_by_base_c():
    c1 = Settings({'k1': 'c1_k1'})
    c2 = Settings({'k1': 'c2_k1', 'k2': 'c2_k2'}, k3='c2_k3')
    c1.update(c2)
    assert len(c1) == 3
    assert c1['k1'] == 'c2_k1'
    assert c1['k2'] == 'c2_k2'
    assert c1['k3'] == 'c2_k3'


def test_copy():
    c1 = Settings({'dict': {'k': 'v'}})
    c2 = c1.copy()
    c1['dict']['k'] = 'vv'
    assert c2['dict']['k'] == 'v'


def test_delete():
    c = Settings({'k1': 'v1', 'k2': 'v2', 'k3': 'v3'})
    c.delete('k2')
    assert len(c) == 2 and 'k2' not in c
    c.delete('k1')
    assert len(c) == 1 and 'k1' not in c
    del c['k3']
    assert len(c) == 0 and 'k3' not in c


def test_setdefault():
    c = Settings()
    c.setdefault('k1', 'v1')
    assert c['k1'] == 'v1'
    c.setdefault('k1', 'v2')
    assert c['k1'] == 'v1'
