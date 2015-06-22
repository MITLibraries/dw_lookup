from __future__ import absolute_import
import cx_Oracle
from author_lookup.config import Config

class DWService(object):
    def __init__(self):
        cfg = Config()
        dsn = cx_Oracle.makedsn(cfg['ORACLE_HOST'], cfg['ORACLE_PORT'], cfg['ORACLE_SID'])
        self.conn = cx_Oracle.connect(cfg['ORACLE_USER'], cfg['ORACLE_PASSWORD'], dsn)
        self.singleNameCursor = self.conn.cursor()
        self.shortSingleNameCursor = self.conn.cursor()
        self.multipleNameCursor = self.conn.cursor()

        # if the user provides a single unbroken letter string
        # just find all names with that string
        # eg *[name_partial]*
        self.singleNameCursor.prepare("""
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

        # if the user provides an extremely short letter string
        # assume it's a complete first or last name
        self.shortSingleNameCursor.prepare("""
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

        ## if the user provides multiple words, either:
        # last, first [optionally more]
        # first [optionally more] last
        # we search for:
        # first [optionally more]* AND last*
        # note that we assume the user is specifying the beginning of each
        self.multipleNameCursor.prepare("""
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

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.singleNameCursor.close()
        self.multipleNameCursor.close()
        self.conn.close()

    def get_data(self, name_partial):
    	data = {'results': []}
        print name_partial
    	res = self.executeQuery(name_partial)

    	for item in res:
    		data['results'].append({
    			'name': item[0],
    			'dept': item[1],
                'mit_id': item[2],
                'start_date': item[3],
                'end_date': item[4]
    		})

    	return data

    def executeQuery(self, name_partial):
        name_partial = name_partial.lower().strip()

        # reject these
        if (len(name_partial) < 2):
            return None

        # for comma delimited strings
        # the first string is the last name
        # the rest is assumed to be the first name
        name_array = name_partial.split(',', 1)

        if len(name_array) > 1:
            name_hash = {
                'first_name_partial': name_array[1].strip() +'%',
                'last_name_partial': name_array[0].strip() +'%'
            }

            return self.multipleNameCursor.execute(None, name_hash).fetchall()

        # for multiple strings broken by spaces
        # the last string is assumed to be the last name
        # the rest is assumed to be the first name
        name_array = name_partial.rsplit(' ', 1)

        if len(name_array) > 1:
            name_hash = {
                'first_name_partial': name_array[0] +'%',
                'last_name_partial': name_array[1] +'%'
            }

            return self.multipleNameCursor.execute(None, name_hash).fetchall()


        # for very short strings w/o commas or spaces
        # assume it's a complete first or last name
        if (len(name_partial) < 3):
            name_hash = {'name_partial': name_partial}

            return self.shortSingleNameCursor.execute(None, name_hash).fetchall()

        # all other cases
        name_hash = {'name_partial': '%'+ name_partial +'%'}
        
        return self.singleNameCursor.execute(None, name_hash).fetchall()