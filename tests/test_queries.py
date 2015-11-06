# -*- coding: utf-8 -*-
from __future__ import absolute_import

from author_lookup.dw import DWService

import py.test

def test_basic():
    expected = {
        "results": {
            "920249105": {
                "depts": {
                    "Libraries": {
                        "Admin Staff": {
                            "end_date": "2999-12", 
                            "start_date": "2014-09"
                        }
                    }
                }, 
                "mit_id": "920249105", 
                "name": "Zendeh, Solh", 
                "name_variants": {}
            }
        }
    }

    with DWService() as dw_service:
        data_returned = dw_service.get_data('solh zendeh')
        assert data_returned == expected