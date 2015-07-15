from __future__ import absolute_import
import cx_Oracle
from author_lookup.config import Config

class DWService(object):
    def __init__(self):
        cfg = Config()
        dsn = cx_Oracle.makedsn(cfg['ORACLE_HOST'], cfg['ORACLE_PORT'], cfg['ORACLE_SID'])
        self.conn = cx_Oracle.connect(cfg['ORACLE_USER'], cfg['ORACLE_PASSWORD'], dsn)
        self.partialSingleNameCursor = self.conn.cursor()
        self.completeSingleNameCursor = self.conn.cursor()
        self.partialFirstPartialLastCursor = self.conn.cursor()
        self.partialFirstCompleteLastCursor = self.conn.cursor()

        self.partialSingleNameCursor.prepare("""
        SELECT
            FULL_NAME,
            DEPARTMENT_NAME,
            MIT_ID,
            START_DATE,
            END_DATE
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
            END_DATE
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

        self.partialFirstPartialLastCursor.prepare("""
        SELECT
            FULL_NAME,
            DEPARTMENT_NAME,
            MIT_ID,
            START_DATE,
            END_DATE
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

        self.partialFirstCompleteLastCursor.prepare("""
        SELECT
            FULL_NAME,
            DEPARTMENT_NAME,
            MIT_ID,
            START_DATE,
            END_DATE
        FROM
            library_person_lookup
        WHERE
            lower(FIRST_NAME) like :first_name_partial AND
            lower(LAST_NAME) = :last_name
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
        self.partialFirstPartialLastCursor.close()
        self.partialFirstCompleteLastCursor.close()
        self.conn.close()

    def get_data(self, name_string):
    	data = {'results': []}
        print name_string
    	res = self.executeQuery(name_string)

    	for item in res:
    		data['results'].append({
    			'name': item[0],
    			'dept': item[1],
                'mit_id': item[2],
                'start_date': item[3],
                'end_date': item[4]
    		})

    	return data

    def executeQuery(self, name_string):
        name_string = name_string.lower().strip()
        print len(name_string)
        # reject these
        if (len(name_string) < 2):
            return []

        # for comma delimited strings
        # the first string is the complete last name
        # the rest is assumed to be the first name
        name_array = name_string.split(',', 1)

        if len(name_array) > 1:
            name_hash = {
                'first_name_partial': name_array[1].strip() +'%',
                'last_name': name_array[0].strip()
            }

            return self.partialFirstCompleteLastCursor.execute(None, name_hash).fetchall()

        # for multiple strings broken by spaces
        # the last string is assumed to be the last name
        # the rest is assumed to be the first name
        name_array = name_string.rsplit(' ', 1)

        if len(name_array) > 1:
            name_hash_single = {'name_partial': '%'+ name_string +'%'}

            singleStringRes = self.partialSingleNameCursor.execute(None, name_hash_single).fetchall()

            name_hash_multiple = {
                'first_name_partial': name_array[0] +'%',
                'last_name_partial': name_array[1] +'%'
            }

            return singleStringRes + self.partialFirstPartialLastCursor.execute(None, name_hash_multiple).fetchall()


        # for very short strings w/o commas or spaces
        # assume it's a complete first or last name
        if (len(name_string) < 3):
            name_hash = {'name_partial': name_string}

            return self.completeSingleNameCursor.execute(None, name_hash).fetchall()

        # all other cases
        name_hash = {'name_partial': '%'+ name_string +'%'}

        return self.partialSingleNameCursor.execute(None, name_hash).fetchall()