# -*- coding: utf-8 -*-
from __future__ import absolute_import

from dw_lookup.dw import DWService
from mock import Mock, patch

import pytest

sample_query_obj = {
    'first': 'solh',
    'last': 'zendeh'
}

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

def test_search_authors():
    with DWService() as dw_service:
        dw_service.multipleNameCursor = Mock()
        dw_service.multipleNameCursor.execute.return_value.fetchall.return_value = sample_db_response
        assert dw_service.search_authors(sample_query_obj) == sample_processed_response

def test_process_response():
    with DWService() as dw_service:
        assert dw_service.process_response(sample_db_response) == sample_processed_response

def test_preprocess_string():
    with DWService() as dw_service:
        assert dw_service.preprocess_string('Testing') == 'testing'
        assert dw_service.preprocess_string('Testing.test') == 'testingtest'