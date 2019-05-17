# RawQuery
Python package to deal with raw sql queries in projects.


Django raw query is a simple wrapper on top of django connection framework, to deal with named parameters in raw sql formatting, few db drivers support this and some don't.

To execute a raw query we use string formatting in serverside, we send the equal number of parameters along with the query.

    SELECT
      IF(create_date = %s, val_one, val_two) AS select_one,
      IF(condition_3=%s, val_three, IF(condition_3=%s, val_four, NULL)) AS select_two
    FROM table_name
    WHERE
      create_date BETWEEN %s AND %s
      condition_2 = %s AND
      condition_3 IN (%s, %s)

In a situation as defined above, we endup defining many duplicate values. If we name the params...

    SELECT
      IF(create_date = %s(start_date), val_one, val_two) AS select_one,
      IF(condition_3=%s(value_one), val_three, IF(condition_3=%s(value_two), val_four, NULL)) AS select_two
    FROM table_name
    WHERE
      create_date BETWEEN %s(start_date) AND %s(end_date)
      condition_2 = %s(condition_two_value) AND
      condition_3 IN (%s(value_one), %s(value_two))

The params are (`start_date`, `value_one`, `start_date`, `end_date`, `condition_two_value`, `value_one`, `value_two`). Here we've duplicate values present in the params list, if we scale this up and your query might have 300 params and 100 of them are duplicate, it's still easy to form the params list but unnecessary effort and not readable.

To solve the above situation, we just pass the `kwargs` instead `positional args`, will and we manage them internally to convert back to positional.

    SELECT
      IF(create_date = {start_date}, val_one, val_two) AS select_one,
      IF(condition_3={cond_three_value_one}, val_three, IF(condition_3={cond_three_value_two}, val_four, NULL)) AS select_two
    FROM table_name
    WHERE
      create_date BETWEEN {start_date} AND {end_date}
      condition_2 = {condition_two_value} AND
      condition_3 IN ({cond_three_value_one}, {cond_three_value_two})

Django raw query uses python formatting style to name the params, it just takes a alpha numerics with just `_` allowed.

For the above query the params part would be...

    params = {
        'start_date': '2019-01-01',
        'end_date': '2019-04-30',
        'condition_two_value': 'condition_two_value ewye33',
        'cond_three_value_one': 'cond_three_value_one 3cewwcw24',
        'cond_three_value_two': 'cond_three_value_two cbehw24'
    }

What Django raw query does here is, it checks for the position of each name in the query and make a list corresponding to it and convert this completely to a positional param query and send it to the server.

It converts the query back to positional based params..

    SELECT
      IF(create_date = %s, val_one, val_two) AS select_one,
      IF(condition_3=%s, val_three, IF(condition_3=%s, val_four, NULL)) AS select_two
    FROM table_name
    WHERE
      create_date BETWEEN %s AND %s
      condition_2 = %s AND
      condition_3 IN (%s, %s)

And the params will be converted as a list with positiona of the parameter maintained.

    `('2019-01-01', 'condition_two_value ewye33', '2019-01-01', '2019-04-30', 'condition_two_value ewye33', 'cond_three_value_one 3cewwcw24', 'cond_three_value_two cbehw24')`

So, process happens irrespective of `db` that we use.
