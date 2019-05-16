# RawQuery
Python package to deal with raw sql queries in projects.


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