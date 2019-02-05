import os
import re

import cx_Oracle


os.environ['NLS_LANG'] = '.AL32UTF8'
mit_regex = re.compile(r'^\d+$')
non_ascii_regex = re.compile(r'[^\x00-\x7F]')


class _DB:
    _conn = None
    _cursor = None

    def configure(self, host, port, sid, user, password):
        self.user = user
        self.password = password
        self.dsn = cx_Oracle.makedsn(host, port, sid)

    @property
    def conn(self):
        self._conn = self._conn or cx_Oracle.connect(self.user,
                                                     self.password,
                                                     self.dsn)
        return self._conn

    @property
    def cursor(self):
        self._cursor = self._cursor or self.conn.cursor()
        return self._cursor

    def select(self, sql, **kwargs):
        return self.cursor.execute(sql, **kwargs)


db = _DB()


def get_orcid(mit_id):
    res = []
    if (mit_regex.search(mit_id) is None):
        return format_response(res)

    res = db.select(SQL_ORCID_BY_ID, mit_id=mit_id).fetchone()
    data = {'results': {'orcid': ''}}

    if res is not None:
        data['results']['orcid'] = res[0]
    return data


def get_author(mit_id):
    res = []
    if (mit_regex.search(mit_id) is None):
        return format_response(res)

    res = db.select(SQL_AUTHOR_BY_ID, mit_id=mit_id).fetchall()

    return format_response(res)


def search_authors(first="", last=""):
    res = []

    if not first and not last:
        return format_response(res)

    first, last = first.lower(), last.lower()
    first_name, last_name = wildcard(first), wildcard(last)

    if first != first_name or last != last_name:
        query = SQL_MULTIPLE_NAME_WILDCARD
    else:
        query = SQL_MULTIPLE_NAME

    res = db.select(query, first_name=first_name, last_name=last_name)\
            .fetchall()

    return format_response(res)


def wildcard(name_string):
    # wildcard all periods
    name_string = name_string.replace('.', r'.?')

    # wildcard all dashes
    name_string = name_string.replace('-', r'[- ]?')

    # wildcard diacritics, etc
    name_string = non_ascii_regex.sub('.', name_string)

    return name_string


def format_response(res):
    data = {'results': {}}

    for item in res:
        name = item[0]
        dept = item[1] or 'NOT SPECIFIED'
        mit_id = item[2] or 'NOT SPECIFIED'
        start_date = item[3]
        end_date = item[4]
        type = item[5] or 'NOT SPECIFIED'
        full_name_variant = item[6]
        orcid_id = item[7] or ''

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


SQL_AUTHOR_BY_ID = '''
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
'''

SQL_ORCID_BY_ID = '''
    SELECT orcid
    FROM orcid_to_mitid
    WHERE mit_id = :mit_id
'''

SQL_MULTIPLE_NAME = '''
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
'''  # noqa: E501

SQL_MULTIPLE_NAME_WILDCARD = '''
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
'''  # noqa: E501
