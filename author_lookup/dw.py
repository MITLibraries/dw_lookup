from __future__ import absolute_import

from author_lookup.config import Config
from nameparser import HumanName

import cx_Oracle
import os
import re

class DWService(object):
    def __init__(self):
        cfg = Config()
        
        dsn = cx_Oracle.makedsn(cfg['ORACLE_HOST'], cfg['ORACLE_PORT'], cfg['ORACLE_SID'])

        # NOTE, these must be set in the environment!
        user = os.environ.get('ORACLE_USER')
    	pw = os.environ.get('ORACLE_PASSWORD')
        
        self.conn = cx_Oracle.connect(user, pw, dsn)

        self.multipleNameCursor = self.conn.cursor()

        self.multipleNameCursor.prepare("""
        (
        SELECT
            library_person_lookup.full_name as full_name,
            library_person_lookup.department_name as department_name,
            library_person_lookup.mit_id,
            to_char(library_person_lookup.start_date, 'yyyy-mm') as start_date,
            to_char(library_person_lookup.end_date, 'yyyy-mm') as end_date,
            library_person_lookup.person_type,

            library_name_variant.full_name as full_name_variant
        FROM
            library_name_variant right outer join
            library_person_lookup on
            library_name_variant.mit_id=library_person_lookup.mit_id
        WHERE
            lower(library_person_lookup.first_name) like :first_name_partial ||'%' AND
            lower(library_person_lookup.last_name) like :last_name_partial ||'%'
        )
        UNION
        (
        SELECT
            library_person_lookup.full_name as full_name,
            library_person_lookup.department_name as department_name,
            library_person_lookup.mit_id,
            to_char(library_person_lookup.start_date, 'yyyy-mm') as start_date,
            to_char(library_person_lookup.end_date, 'yyyy-mm') as end_date,
            library_person_lookup.person_type,

            library_name_variant.full_name as full_name_variant
        FROM
            library_name_variant,
            library_person_lookup
        WHERE
            lower(library_name_variant.full_name) like '%, '|| :first_name_partial ||' %' AND
            lower(library_name_variant.full_name) like :last_name_partial ||'%' AND
            library_name_variant.mit_id=library_person_lookup.mit_id
        )
        ORDER BY
            full_name
        """)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.multipleNameCursor.close()
        self.conn.close()

    def search_authors(self, query_obj):
        res = []

        if ('first' in query_obj and 'last' in query_obj):
            name_hash = {
                'first_name_partial': self.preprocess_string(query_obj['first']),
                'last_name_partial': self.preprocess_string(query_obj['last'])
            }

            # first or last name should be >1 char after preprocessing
            if (    len(name_hash['first_name_partial']) > 1 or
                    len(name_hash['last_name_partial']) > 1):
                res = self.multipleNameCursor.execute(None, name_hash).fetchall()
        
        return self.process_response(res)

    def process_response(self, res):
        data = {'results': {}}

        for item in res:
            name = item[0]
            dept = item[1]
            mit_id = item[2]
            start_date = item[3]
            end_date = item[4]
            type = item[5]
            full_name_variant = item[6]

            if mit_id not in data['results']:
                data['results'][mit_id] = {
                    'name': name,
                    'mit_id': mit_id,
                    'depts': {},
                    'name_variants': {}
                }

            result_obj = data['results'][mit_id]

            if dept not in result_obj['depts']:
                result_obj['depts'][dept] = {}

            if type not in result_obj['depts'][dept]:
                result_obj['depts'][dept][type] = {
                    'start_date': start_date,
                    'end_date': end_date
                }

            if (    full_name_variant and
                    (full_name_variant not in result_obj['name_variants'])):
                result_obj['name_variants'][full_name_variant] = True

        return data

    def preprocess_string(self, name_string):
        # remove all caps
        name_string = name_string.lower()

        # remove all periods
        name_string = name_string.replace(".", "")

        return name_string
