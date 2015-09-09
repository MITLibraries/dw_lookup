from __future__ import absolute_import

import cx_Oracle
import re
from author_lookup.config import Config

class DWService(object):
    def __init__(self):
        cfg = Config()
        dsn = cx_Oracle.makedsn(cfg['ORACLE_HOST'], cfg['ORACLE_PORT'], cfg['ORACLE_SID'])
        self.conn = cx_Oracle.connect(cfg['ORACLE_USER'], cfg['ORACLE_PASSWORD'], dsn)
        self.partialSingleNameCursor = self.conn.cursor()
        self.completeSingleNameCursor = self.conn.cursor()
        self.multipleNameCursor = self.conn.cursor()

        self.partialSingleNameCursor.prepare("""
        SELECT
            FULL_NAME,
            DEPARTMENT_NAME,
            MIT_ID,
            START_DATE,
            END_DATE,
            PERSON_TYPE
        FROM
            library_person_lookup
        WHERE
            lower(FULL_NAME) like :name_partial
        ORDER BY
            Full_NAME,
            END_DATE DESC,
            DEPARTMENT_NAME
        """)

        self.completeSingleNameCursor.prepare("""
        SELECT
            FULL_NAME,
            DEPARTMENT_NAME,
            MIT_ID,
            START_DATE,
            END_DATE,
            PERSON_TYPE
        FROM
            library_person_lookup
        WHERE
            lower(FIRST_NAME) = :name_partial OR
            lower(LAST_NAME) = :name_partial
        ORDER BY
            Full_NAME,
            END_DATE DESC,
            DEPARTMENT_NAME
        """)

        self.multipleNameCursor.prepare("""
        SELECT
            FULL_NAME,
            DEPARTMENT_NAME,
            MIT_ID,
            START_DATE,
            END_DATE,
            PERSON_TYPE
        FROM
            library_person_lookup
        WHERE
            lower(FIRST_NAME) like :first_name_partial AND
            lower(LAST_NAME) like :last_name_partial
        ORDER BY
            Full_NAME,
            END_DATE DESC,
            DEPARTMENT_NAME
        """)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.partialSingleNameCursor.close()
        self.completeSingleNameCursor.close()
        self.multipleNameCursor.close()
        self.conn.close()

    def get_data(self, name_string):
    	data = {'results': []}
    	res = self.execute_query(name_string)

    	for item in res:
    		data['results'].append({
    			'name': item[0],
    			'dept': item[1],
                'mit_id': item[2],
                'start_date': item[3],
                'end_date': item[4],
                'type': item[5]
    		})

    	return data

    def process_name_string(self, name_string):
        name_string = name_string.lower()
        name_string = name_string.strip()

        return name_string

    def process_first_name(self, first_name_partial):
        first_name_partial = first_name_partial.strip().split(' ', 1)[0]

        return first_name_partial

    def process_last_name(self, last_name_partial):
        last_name_partial = re.sub(r'\b(jr\.?|iii)$', '', last_name_partial)
        last_name_partial = last_name_partial.strip()

        return last_name_partial

    def execute_query(self, name_string):
        name_string = self.process_name_string(name_string)
        print name_string
        # reject these
        if (len(name_string) < 2):
            return []

        # for comma delimited strings
        # the string before the comma is a partial last name
        # the first string after the comma is assumed to be a partial first
        # for now, we ignore the rest of the string
        name_array = name_string.split(',', 1)

        if len(name_array) > 1:
            name_hash = {
                'first_name_partial': self.process_first_name(name_array[1]) +'%',
                'last_name_partial': self.process_last_name(name_array[0]) +'%'
            }
            print name_hash
            return self.multipleNameCursor.execute(None, name_hash).fetchall()

        # for multiple strings broken by spaces
        # the last string is assumed to be a partial last name
        # the first string is assumed to be the first name
        # for now, we are ignoring any interstitial strings
        name_array = name_string.split(' ')

        if len(name_array) > 1:
            name_hash_single = {'name_partial': '%'+ name_string +'%'}

            singleStringRes = self.partialSingleNameCursor.execute(None, name_hash_single).fetchall()

            name_hash_multiple = {
                'first_name_partial': self.process_last_name(name_array[0]) +'%',
                'last_name_partial': self.process_last_name(name_array[-1]) +'%'
            }

            return singleStringRes + self.multipleNameCursor.execute(None, name_hash_multiple).fetchall()


        # for very short strings w/o commas or spaces
        # assume it's a complete first or last name
        if (len(name_string) < 3):
            name_hash = {'name_partial': name_string}

            return self.completeSingleNameCursor.execute(None, name_hash).fetchall()

        # all other cases
        name_hash = {'name_partial': '%'+ name_string +'%'}

        return self.partialSingleNameCursor.execute(None, name_hash).fetchall()
