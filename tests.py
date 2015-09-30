#!flask/bin/python
import json
import os
import unittest

from author_lookup.dw import DWService

class TestCase(unittest.TestCase):
    def setUp(self):
        print "setup"

    def tearDown(self):
        print "teardown"

    def test_basic(self):
        expected = '{"results": {"920249105": {"mit_id": "920249105", "depts": {"Libraries": {"null": {"start_date": "2014-09", "end_date": "2999-12"}}}, "name_variants": {}, "name": "Zendeh, Solh"}}}'
        with DWService() as dw_service:
            data_returned = json.dumps(dw_service.get_data('solh zendeh'))
            print 'expected:', expected
            print 'data_returned:', data_returned
            assert data_returned == expected



if __name__ == '__main__':
    unittest.main()