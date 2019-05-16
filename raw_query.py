# Copyright (c) 2019-2020 by Srinivas Garlapati - gsb@gsb-eng.com

"""
Module to serve raw query executions in django framework.
"""

# Maintain dictionary order for imports.
import logging
import re

from django.db import connections

logger = logging.getLogger(__name__)


class RawQuery(object):
    """
    Class to deal with raw query executions.
    """
    def __init__(self, query, db_name='default', params=None):
        """
        Initializer.

        :param string query: SQL Query.
        :param string data_style: list/dict.
        """
        self.connection = connections[db_name]
        self.cursor = self.connection.cursor()
        self.__results = None
        self.query = query
        self.description = None
        self.params = params

    def execute(self, commit=False):
        """
        Method to execute the raw query.
        """
        if self.params:
            self._replace_dict_params()
        elif self.params is None:
            self.params = {}

        self.cursor.execute(self.query, self.params)
        if commit:
            self.connection.commit()
        else:
            self.__results = self.cursor.fetchall()
        return self

    def fetch(self, like='list'):
        """
        Method to extract data from cursor.

        :param string like: How data needs to presented.
        :returns list: A list of dicts or tuples based on the like flag.

        I.e:
            If like == 'list'
            returns:
                [
                    (val1, val2, val3),
                    (val1, val2, val3)
                ]

            if like == 'dict'
            returns:
                [
                    {'val1': val1, 'val2': val2, 'val3': val3},
                    {'val1': val1, 'val2': val2, 'val3': val3},
                ]
        """
        # If user preferred to get dict, this logic helps in converting
        # data nterms of dict by using cursor description object.
        if like == 'dict':

            temp_result = []
            columns = [col[0] for col in self.cursor.description]
            for row in self.__results:
                temp_result.append(dict(zip(columns, row)))
            return temp_result

        return self.__results

    def _replace_dict_params(self):
        """
        Method to deal with dict params.

        We are trying to use dict instead of tuple of values, so that we don't
        need to worry about param positioning. This really helps in building
        dynamic queries you don't need to check for the param positioning.

        I.e:
            In general normal queries will be written like below..

            SQL = '''
                SELECT
                   COLUMN1,
                   COLUMN2,
                   %s AS TEMP_COLUMN
                FROM table as t
                WHERE
                    t.COLUMN3 = %s AND
                    t.COLUMN_N in %s
            '''
            params = ('TEMP COLUMN VALUE', 'COLUMNS3', (1, 2, 3))

            And the above query gets passed to the cursor like below..

            couror.execute(SQL, params)

            This will protect from SQL injection attacks, but if have to build a
            dynamic query it's a becomes a problem to create a final params
            tuple with exact positioning.

        Just to overcome the above problem, we've introduced this method in
        RawQuery to automate the above param positioning part.

        I.e:
            >>> from ... import RawQuery
            >>> SQL =
            '''
                  SELECT
                    COLUMN1,
                    COLUMN2,
                    {temp_value} AS TEMP_COLUMN
                  FROM table as t
                  WHERE
                    t.COLUMN3 = {col3_value} AND
                    t.COLUMN_N in {coln_value_list}
                    '''
            >>> params = {'temp_value': 'Temp Value', 'col3_value': 3,
                          'coln_value_list': (1, 2, 3)}

            Then try with "RawQuery"...

            >>> query = RawQuery(SQL, params=params)
            >>> quer, para = query._replace_dict_params()
            >>> print quer

              SELECT
                COLUMN1,
                COLUMN2,
                %s AS TEMP_COLUMN
              FROM table as t
              WHERE
                t.COLUMN3 = %s AND
                t.COLUMN_N in %s

            >>> print para
            ['Temp Value', 3, (1, 2, 3)]

        The above dict format of attributes gets converted into a tuple of
        values.
        """

        # This is the reqular expression to identify all the probable matches
        # in the given query which are following
        #
        #        {attr_name}/{attrname}/{attr-name}
        #
        reg_ex = re.compile('(?:\{\w+[_-]*\w+\})')

        # Find all the patches
        all_patches = reg_ex.findall(self.query)

        # Creates the params list using patches.
        self.params = [self.params[i.strip('{|}')] for i in all_patches]

        # Substitue '%s' inplace of all the {attr_names}.
        self.query = reg_ex.sub('%s', self.query)
        return self.query, self.params
