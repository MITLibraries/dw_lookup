# -*- coding: utf-8 -*-
from __future__ import absolute_import

from dw_lookup.config import Config
from nameparser import HumanName

import cx_Oracle
import os
import re

class DWService(object):
    def __init__(self):
        cfg = Config()

        # precompile all regex
        self.mitIdMatch = re.compile(r'^\d+$')
        self.nonAsciiMatch = re.compile(r'[^\x00-\x7F]')

        # NOTE, these must be set in the environment!
        user = os.environ.get('ORACLE_USER')
        pw = os.environ.get('ORACLE_PASSWORD')

        # might be better id this was as well
        os.environ["NLS_LANG"] = ".AL32UTF8"
        
        dsn = cx_Oracle.makedsn(cfg['ORACLE_HOST'], cfg['ORACLE_PORT'], cfg['ORACLE_SID'])
        
        self.conn = cx_Oracle.connect(user, pw, dsn)

        self.authorByIdCursor = self.conn.cursor()
        self.multipleNameCursor = self.conn.cursor()
        self.multipleNameCursorWildcard = self.conn.cursor()

        self.authorByIdCursor.prepare("""
        SELECT
            library_person_lookup.full_name as full_name,
            library_person_lookup.department_name as department_name,
            library_person_lookup.mit_id,
            to_char(library_person_lookup.start_date, 'yyyy-mm') as start_date,
            to_char(library_person_lookup.end_date, 'yyyy-mm') as end_date,
            library_person_lookup.person_type,

            library_name_variant.full_name as full_name_variant,

            orcid_to_mitid.orcid as orcid_id
        FROM
            library_person_lookup
                left outer join library_name_variant on
                    library_name_variant.mit_id=library_person_lookup.mit_id
                left outer join orcid_to_mitid on
                    orcid_to_mitid.mit_id=library_person_lookup.mit_id
        WHERE
            library_person_lookup.mit_id = :mit_id
        """)

        self.multipleNameCursor.prepare("""
        (
        SELECT
            library_person_lookup.full_name as full_name,
            library_person_lookup.department_name as department_name,
            library_person_lookup.mit_id,
            to_char(library_person_lookup.start_date, 'yyyy-mm') as start_date,
            to_char(library_person_lookup.end_date, 'yyyy-mm') as end_date,
            library_person_lookup.person_type,

            library_name_variant.full_name as full_name_variant,

            orcid_to_mitid.orcid as orcid_id
        FROM
            library_person_lookup
                left outer join library_name_variant on
                    library_name_variant.mit_id=library_person_lookup.mit_id
                left outer join orcid_to_mitid on
                    orcid_to_mitid.mit_id=library_person_lookup.mit_id
        WHERE
            lower(library_person_lookup.first_name) like :first_name ||'%' AND
            lower(library_person_lookup.last_name) like :last_name ||'%'
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

            library_name_variant.full_name as full_name_variant,

            orcid_to_mitid.orcid as orcid_id
        FROM
            library_name_variant,
            library_person_lookup
                left outer join orcid_to_mitid on
                    orcid_to_mitid.mit_id=library_person_lookup.mit_id
        WHERE
            lower(library_name_variant.full_name) like '%, '|| :first_name ||'%' AND
            lower(library_name_variant.full_name) like :last_name ||'%' AND
            library_name_variant.mit_id=library_person_lookup.mit_id
        )
        ORDER BY
            full_name
        """)

        self.multipleNameCursorWildcard.prepare("""
        (
        SELECT
            library_person_lookup.full_name as full_name,
            library_person_lookup.department_name as department_name,
            library_person_lookup.mit_id,
            to_char(library_person_lookup.start_date, 'yyyy-mm') as start_date,
            to_char(library_person_lookup.end_date, 'yyyy-mm') as end_date,
            library_person_lookup.person_type,

            library_name_variant.full_name as full_name_variant,

            orcid_to_mitid.orcid as orcid_id
        FROM
            library_person_lookup
                left outer join library_name_variant on
                    library_name_variant.mit_id=library_person_lookup.mit_id
                left outer join orcid_to_mitid on
                    orcid_to_mitid.mit_id=library_person_lookup.mit_id
        WHERE
            REGEXP_LIKE(lower(library_person_lookup.first_name), :first_name ||'.*') AND
            REGEXP_LIKE(lower(library_person_lookup.last_name), :last_name ||'.*')
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

            library_name_variant.full_name as full_name_variant,

            orcid_to_mitid.orcid as orcid_id
        FROM
            library_name_variant,
            library_person_lookup
                left outer join orcid_to_mitid on
                    orcid_to_mitid.mit_id=library_person_lookup.mit_id
        WHERE
            REGEXP_LIKE(lower(library_name_variant.full_name), '.+, '|| :first_name ||'.*') AND
            REGEXP_LIKE(lower(library_name_variant.full_name), :last_name ||'.*') AND
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

    def get_author(self, query_obj):
        res = []

        if ('mit_id' not in query_obj):
            return self.format_response(res)

        if (self.mitIdMatch.search(query_obj['mit_id']) is None):
            return self.format_response(res)

        query_hash = {
            'mit_id': query_obj['mit_id']
        }

        res = self.authorByIdCursor.execute(None, query_hash).fetchall()
        
        return self.format_response(res)

    def search_authors(self, query_obj):
        res = [] 

        if ('first' not in query_obj or 'last' not in query_obj):
            return self.format_response(res)

        first_name = self.preprocess_string(query_obj['first'])
        last_name= self.preprocess_string(query_obj['last'])

        if (len(first_name) == 0 and
            len(last_name) == 0):
            return self.format_response(res)

        query_hash = {
            'first_name': self.wildcard_string(first_name),
            'last_name' : self.wildcard_string(last_name)
        }

        cursor = self.multipleNameCursor

        # if there are wildcards, use special sql    
        if (first_name != query_hash['first_name'] or
            last_name != query_hash['last_name']):
            cursor = self.multipleNameCursorWildcard

        res = cursor.execute(None, query_hash).fetchall()
        
        return self.format_response(res)

    def format_response(self, res):
        data = {'results': {}}

        for item in res:
            name = item[0]
            dept = item[1]
            mit_id = item[2]
            start_date = item[3]
            end_date = item[4]
            type = item[5]
            full_name_variant = item[6]
            orcid_id = item[7] or ""

            if mit_id not in data['results']:
                data['results'][mit_id] = {
                    'name': name,
                    'mit_id': mit_id,
                    'depts': {},
                    'name_variants': {},
                    'orcid_id': orcid_id
                }

            result_obj = data['results'][mit_id]

            if dept not in result_obj['depts']:
                result_obj['depts'][dept] = {}

            if type not in result_obj['depts'][dept]:
                result_obj['depts'][dept][type] = {
                    'start_date': start_date,
                    'end_date': end_date
                }

            if (full_name_variant and
                (full_name_variant not in result_obj['name_variants'])):
                result_obj['name_variants'][full_name_variant] = True

        return data

    def preprocess_string(self, name_string):
        # remove all caps
        name_string = name_string.lower()

        return name_string

    def wildcard_string(self, name_string):
        # wildcard all periods
        name_string = name_string.replace(".", r".?")

        # wildcard all dashes
        name_string = name_string.replace("-", r"[- ]?")

        # wildcard diacritics, etc
        name_string = self.nonAsciiMatch.sub('.', name_string)

        print name_string

        return name_string
