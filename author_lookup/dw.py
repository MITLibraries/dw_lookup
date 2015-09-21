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

    def execute_query(self, name_string):
        name_string = name_string.lower()
        print "name_string: "+ name_string
        print "HumanName: "+ str(HumanName(name_string))
        print HumanName(name_string).as_dict()

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
                'first_name_partial': parsed_name_string.first +'%',
                'last_name_partial': parsed_name_string.last +'%'
            }

            return self.multipleNameCursor.execute(None, name_hash).fetchall()

        # single name, longer than 3 chars
        name_hash = {'name_partial': '%'+ name_string +'%'}

        return self.partialSingleNameCursor.execute(None, name_hash).fetchall()
