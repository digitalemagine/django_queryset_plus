#### using psycopg2 directly... since it's our db! could be an option. But requires to initialize the connection.
#

import re
import psycopg2, psycopg2.extras
from django.conf import settings



def various_staff(qs):
    # Will work on both related and prefetch.
    # Related with joins, prefetch one by one. Let's try.

        # my own simple ORM... this does not build back into a model instance, just dicts.
    #
    '''
    normal query
    SELECT "music_album"."id", "music_album"."user_id", "music_album"."creation_datetime", "music_album"."modification_datetime", "music_album"."url", "music_album"."title", "music_album"."published_date", "music_album"."country", "music_album"."artist_id" FROM "music_album" LIMIT 21
    prefetch query:
    SELECT ("music_album_images"."album_id") AS "_prefetch_related_val_album_id", "media_image"."id", "media_image"."user_id", "media_image"."creation_datetime", "media_image"."modification_datetime", "media_image"."url", "media_image"."thumbnail", "media_image"."width", "media_image"."height" FROM "media_image" INNER JOIN "music_album_images" ON ( "media_image"."id" = "music_album_images"."image_id" ) WHERE "music_album_images"."album_id" IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21)
    '''
    query = "SELECT {columns} FROM {table}"
    ## additional stuff comes with LIMIT and WHERE
    #model_fields = [f.name for f in ModelClass._meta.concrete_fields]
    model_table = ModelClass._meta.db_table
    columns = ['"%"."%"' % (model_table, f.name, ) for f in ModelClass._meta.concrete_fields]

    prefetch_field = ""
    prefetch_table = "%_%" % (model_table, prefetch_field)

    # the prefetch can be done with prefetch_generic_fk_values and similar codes that should though be hacked to get the queryset with related fields


def queryset_as_values(queryset):
    return



def queryset_as_dict(qs):
    """
    Uses psycopg2 RealDictCursor to provide a /flat/ dictionary
    """

    dict_cur = connect().cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # check if there are some prefetch_related that have to be taken care of separately

    # get the SQL query including select_related
    query = str(qs.query).split('FROM')
    '''
    Django queries come as "app_model"."field" and I rename the columns as "app_model__field".
    '''
    query[0] = re.sub(r'"(\w*)"\."(\w*)"', r'"\1"."\2" AS "\1__\2"', query[0])
    query = 'FROM'.join(query)

    dict_cur.execute(query)

    ## if we need to modify the dicts, that's where it's gonna happen:
    # But maybe in that case it's better /not/ to use the dictcursor, and rather take care of it ourselves.
    return dict_cur.fetchall()


"""
THE FOLLOWING ARE PURE DJANGO TESTS
"""


from itertools import *
from django.db import connection


def queryset_to_dict(qs, manager):
    cursor = connection.cursor()
    print "Ready to execute:"
    print "---"
    print qs.query
    print "---"
    cursor.execute(str(qs.query))  # qs.query.__str__ launches the SQL compiler and replaces the parameters
    print "Results:"
    for row in fetch_to_dict(cursor):
        print row
    print "***"

    # print manager._select_related



def fetchall_to_dict(cursor):
    """
    Returns all rows from a cursor as a dict
    Careful - fetchall retrieves ALL ROWS IN MEMORY
    """
    desc = cursor.description
    cols = [col[0] for col in desc]
    return [
        dict(zip(cols, row)) for row in cursor.fetchall()
    ]


def fetch_to_dict(cursor):
    """
    returns all rows from a cursor as a dict
    - Iterator version (could be improved?)
    """
    desc = cursor.description
    cols = [col[0] for col in desc]
    row = cursor.fetchone()
    while row is not None:
        yield dict(zip(cols, row))
        row = cursor.fetchone()

'''
Or use psycopg2 DictCursor
>>> dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
>>> dict_cur.execute("INSERT INTO test (num, data) VALUES(%s, %s)",
...                  (100, "abc'def"))
>>> dict_cur.execute("SELECT * FROM test")
>>> rec = dict_cur.fetchone()
>>> rec['id']
1
>>> rec['num']
100
>>> rec['data']
"abc'def"
'''
