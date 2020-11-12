from guniflask.utils.string import string_camelcase, string_lowercase_hyphen, \
    string_lowercase_underscore, string_uppercase_underscore


def test_string_camelcase():
    assert string_camelcase('get_http_response') == 'GetHttpResponse'
    assert string_camelcase('meta-data') == 'MetaData'
    assert string_camelcase('N2O') == 'N2O'


def test_string_lowercase_hyphen():
    assert string_lowercase_hyphen('getHTTPResponse') == 'get-http-response'
    assert string_lowercase_hyphen('MetaData') == 'meta-data'


def test_string_lowercase_underscore():
    assert string_lowercase_underscore('getHTTPResponse') == 'get_http_response'
    assert string_lowercase_underscore('MetaData') == 'meta_data'


def test_string_uppercase_underscore():
    assert string_uppercase_underscore('getHTTPResponse') == 'GET_HTTP_RESPONSE'
    assert string_uppercase_underscore('MetaData') == 'META_DATA'
