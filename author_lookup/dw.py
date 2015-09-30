from __future__ import absolute_import

from author_lookup.config import Config
from nameparser import HumanName

import cx_Oracle
import re

class DWService(object):
    def __init__(self):
        cfg = Config()
        dsn = cx_Oracle.makedsn(cfg['ORACLE_HOST'], cfg['ORACLE_PORT'], cfg['ORACLE_SID'])
        self.conn = cx_Oracle.connect(cfg['ORACLE_USER'], cfg['ORACLE_PASSWORD'], dsn)
        self.partialSingleNameCursor = self.conn.cursor()
        self.completeSingleNameCursor = self.conn.cursor()
        self.multipleNameCursor = self.conn.cursor()

        self.partialSingleNameCursor.prepare("""
        (
            SELECT
                library_person_lookup.full_name,
                library_person_lookup.department_name,
                library_person_lookup.mit_id,
                to_char(library_person_lookup.start_date, 'yyyy-mm') as start_date,
                to_char(library_person_lookup.end_date, 'yyyy-mm') as end_date,
                library_person_lookup.person_type,

                library_name_variant.full_name as full_name_variant,
                library_name_variant.name_type
            FROM
                library_name_variant right outer join
                library_person_lookup on
                library_name_variant.mit_id=library_person_lookup.mit_id
            WHERE
                lower(library_person_lookup.first_name) = '%'|| :name_partial ||'%' OR
                lower(library_person_lookup.last_name) = '%'|| :name_partial ||'%'
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
                library_name_variant.name_type
            FROM
                library_name_variant,
                library_person_lookup
            WHERE
                lower(library_name_variant.full_name) like '%'|| :name_partial ||'%' AND
                library_name_variant.mit_id=library_person_lookup.mit_id
        )
        ORDER BY
            full_name
        """)

        self.completeSingleNameCursor.prepare("""
        SELECT
            library_person_lookup.full_name,
            library_person_lookup.department_name,
            library_person_lookup.mit_id,
            to_char(library_person_lookup.start_date, 'yyyy-mm') as start_date,
            to_char(library_person_lookup.end_date, 'yyyy-mm') as end_date,
            library_person_lookup.person_type,

            library_name_variant.full_name as full_name_variant,
            library_name_variant.name_type
        FROM
            library_name_variant right outer join
            library_person_lookup on
            library_name_variant.mit_id=library_person_lookup.mit_id
        WHERE
            lower(library_person_lookup.first_name) = :name_partial OR
            lower(library_person_lookup.last_name) = :name_partial
        ORDER BY
            library_person_lookup.full_name
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
            library_name_variant.name_type
        FROM
            library_name_variant right outer join
            library_person_lookup on
            library_name_variant.mit_id=library_person_lookup.mit_id
        WHERE
            lower(library_person_lookup.first_name) like :first_name_partial ||'%' AND
            lower(library_person_lookup.last_name) like '%'|| :last_name_partial ||'%'
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
            library_name_variant.name_type
        FROM
            library_name_variant,
            library_person_lookup
        WHERE
            lower(library_name_variant.full_name) like '%, '|| :first_name_partial ||' %' AND
            lower(library_name_variant.full_name) like '%'|| :last_name_partial ||'%' AND
            library_name_variant.mit_id=library_person_lookup.mit_id
        )
        ORDER BY
            full_name
        """)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.partialSingleNameCursor.close()
        self.completeSingleNameCursor.close()
        self.multipleNameCursor.close()
        self.conn.close()

    def get_data(self, name_string):
        data = {'results': {}}
        res = self.execute_query(name_string)

        for item in res:
            # create a class for this
            person_obj = {
                'name': item[0],
                'dept': item[1],
                'mit_id': item[2],
                'start_date': item[3],
                'end_date': item[4],
                'type': item[5],
                'full_name_variant': item[6],
                'name_type': item[7]
            }

            results_obj = data['results'].setdefault(person_obj['mit_id'], {
                'name': person_obj['name'],
                'mit_id': person_obj['mit_id'],
                'depts': {},
                'name_variants': {}
            })

            # create an empty hash for this department, if it doesn't exist
            dept_obj = results_obj['depts'].setdefault(person_obj['dept'], {})

            # each person can be involved in a department in different capacities
            # this is called 'type'
            # each type of capacity for each department has a start and end date
            dept_obj[person_obj['type']] = {
                'start_date': person_obj['start_date'],
                'end_date': person_obj['end_date']
            }

            if (person_obj['full_name_variant']):
                # create empty set for this name varient, since there can be multiple types
                name_varient_obj = results_obj['name_variants'].setdefault(person_obj['full_name_variant'], {})
                
                name_varient_obj[person_obj['name_type']] = True

    	return data

    def execute_query(self, name_string):
        name_string = name_string.lower()

        # reject these
        if (len(name_string) < 2):
            return []

        # for very short strings
        # assume it's a complete first or last name
        if (len(name_string) < 3):
            name_hash = {'name_partial': name_string}

            return self.completeSingleNameCursor.execute(None, name_hash).fetchall()

        parsed_name_string = HumanName(name_string)

        # if there is more than a single word
        if (parsed_name_string.first and parsed_name_string.last):
            name_hash = {
                'first_name_partial': parsed_name_string.first,
                'last_name_partial': parsed_name_string.last
            }

            return self.multipleNameCursor.execute(None, name_hash).fetchall()

        # single name, longer than 3 chars
        name_hash = {'name_partial': '%'+ name_string +'%'}

        return self.partialSingleNameCursor.execute(None, name_hash).fetchall()
