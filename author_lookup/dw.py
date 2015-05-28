from __future__ import absolute_import
import cx_Oracle
from author_lookup.config import Config

class DWService(object):
    def __init__(self):
        cfg = Config()
        dsn = cx_Oracle.makedsn(cfg['ORACLE_HOST'], cfg['ORACLE_PORT'], cfg['ORACLE_SID'])
        self.conn = cx_Oracle.connect(cfg['ORACLE_USER'], cfg['ORACLE_PASSWORD'], dsn)
        self.singleNameCursor = self.conn.cursor()
        self.multipleNameCursor = self.conn.cursor()

        # if the user provides a single letter string
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

        ## if the user provides multiple words, either:
        # last, first [optionall more]
        # first [optionsally more] last
        # we search for :
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
        name_array = name_partial.split(',', 1)

        if len(name_array) > 1:
            name_hash = {
                'first_name_partial': name_array[1].lower().strip() +'%',
                'last_name_partial': name_array[0].lower().strip() +'%'
            }

            return self.multipleNameCursor.execute(None, name_hash).fetchall()

        name_array = name_partial.rsplit(' ', 1)

        if len(name_array) > 1:
            name_hash = {
                'first_name_partial': name_array[0].lower().strip() +'%',
                'last_name_partial': name_array[1].lower().strip() +'%'
            }

            return self.multipleNameCursor.execute(None, name_hash).fetchall()

        name_hash = {'name_partial': '%'+ name_partial.lower().strip() +'%'}

        return self.singleNameCursor.execute(None, name_hash).fetchall()