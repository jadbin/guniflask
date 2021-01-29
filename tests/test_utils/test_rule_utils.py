from guniflask.utils.rule import make_ignore_rule_for_field, make_only_rule_for_field, _make_rule_set


def test_make_set():
    assert _make_rule_set('a') == {'a'}
    assert _make_rule_set('a,b') == {'a', 'b'}
    assert _make_rule_set({'a'}) == {'a'}
    assert _make_rule_set(['a', 'b']) == {'a', 'b'}


def test_make_ignore_rule():
    assert make_ignore_rule_for_field('a.b') == {'a.b'}


def test_make_only_rule():
    assert make_only_rule_for_field('a.b') == {'a', 'a.b'}
