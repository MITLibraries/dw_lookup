from unittest.mock import patch

from dw_lookup.dw import search_authors


sample_db_response = [[
    'solh zendeh',
    'test dept',
    12345,
    2345,
    6789,
    'test type',
    'test name varient',
    'abcdefg-123'
]]

sample_processed_response = {
    'results': {
        12345: {
            'name': 'solh zendeh',
            'mit_id': 12345,
            'depts': {
                'test dept': {
                    'test type': {
                        'start_date': 2345,
                        'end_date': 6789
                    }
                }
            },
            'name_variants': {
                'test name varient': True
            },
            'orcid_id': 'abcdefg-123'
        }
    }
}


@patch("dw_lookup.dw.db")
def test_search_authors(mock):
    mock.select.return_value.fetchall.return_value = sample_db_response
    assert search_authors(first="solh", last="zendeh") == \
        sample_processed_response
