import re
import psycopg2, psycopg2.extras

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection  ## used for debug/profiling SQL


def connect():
    """
    Returns a psycopg2 connection based on django.conf settings.
    Or simply uses django.db.connection instead!!

    This function is here only to be able to quickly switch to postgresql
    cursors for comparison
    """
    return connection
    # if this is a test, the database connection
    # is easier to be let managed by django!
    # But the following test detection should still want
    try:
        DB_SETTINGS = settings.DATABASES['default']
        import sys
        if 'test' in sys.argv:
            database_name = DB_SETTINGS.get('TEST_NAME') or 'test_'+DB_SETTINGS.get('NAME')
        else:
            database_name = DB_SETTINGS.get('NAME')
        return psycopg2.connect(
            host=DB_SETTINGS.get('HOST'),
            port=DB_SETTINGS.get('PORT'),
            database=database_name,
            user=DB_SETTINGS.get('USER'),
            password=DB_SETTINGS.get('PASSWORD'),
        )
    except Exception as e:
        print "Could not run psycopg2.connect: ", e
        return connection


def _get_depth(alias_map, alias, depth=None):
    """

    """
    if depth is None:
        depth = []
    #if alias is not None:
    if alias:
        parent = alias_map[alias]
        if parent.join_field:
            depth.append(parent.join_field.name)

        _get_depth(alias_map, parent.lhs_alias, depth)
    return depth[::-1]


def queryset_as_dict(qs):
    """
    Takes a queryset and returns a dictionary-tree structure corresponding to the
    object fields.

    @TODO
    * Add some internal (_) properties eg. including the model name for easier
    following parsing
    * examples of treewalking
    """
    # the following is for easier dev/debug
    # cursor = connect().cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor = connect().cursor()

    # check if there are some prefetch_related that have to be taken care of separately

    # get the SQL query including select_related. This has also the effect of
    # /compiling/ the queryset.query
    # Splits on FROM to allow farther processing
    query = str(qs.query).split('FROM')

    # get related fields and prefetch fields from the queryset:

    extra_names = list(qs.query.extra_select)
    aggregate_names = list(qs.query.aggregate_select)

    if qs.model:
        field_names = [f.attname for f in qs.model._meta.concrete_fields]
    else:
        print "Dont know the model"

    '''
    Uncomment this section for some debugging info
    prl = qs._prefetch_related_lookups
    related = qs.query.select_related
    ### Related is a dict model->fields
    names = extra_names + field_names + aggregate_names
    d = qs.query.__dict__

    ### related_select_cols contains real columns info for the related model.
    assert False
    '''

    '''
    Related fields contain the exact structure of children I am expecting.
    It can be used to delete unnecessary columns for the SQL
    (and, thus, for the serialization)
    '''
    related_fields = qs.query.select_related
    print "related_fields", related_fields

    '''
    Also, the "alias" (alias_map, alias_prefix, alias_refcount) contains the
    table/column names (and aliases) in the query

    join_map is a sort or reversed alias_map (and viceversa of course)
    '''

    alias_map = qs.query.alias_map
    print "Alias map:"
    for k, v in alias_map.items():
        print k, ":\n\t", v

    join_map = qs.query.join_map
    print "Join map:"
    for k, v in join_map.items():
        print k, ":\n\t", v




    '''
    3 ways to get the "MAIN" table:
    # the first table after FROM is the "MAIN" object.
    >>> main_table = re.search('"(\w*)"', query[1]).groups()[0]
    # or:
    >>> qs.model._meta.db_table
    # or
    >>> '{}_{}'.format(qs.model._meta.app_label, qs.model._meta.model_name)
    '''
    main_table = qs.model._meta.db_table

    query[0] = re.sub(r'\s("?)(\w*)("?)\."(\w*)"', r' \1\2\3."\4" AS "\2__\4"', query[0])
    query = 'FROM'.join(query)

    print "--- QUERY ---"
    print query
    print "-------------\n"

    cursor.execute(query)
    desc = cursor.description
    cols = [col[0] for col in desc]

    ## if we need to modify the dicts, that's where it's gonna happen:
    # But maybe in that case it's better /not/ to use the dictcursor, and rather take care of it ourselves.
    rows = cursor.fetchall()

    ### The following is potentially processing intensive if there are a lot of results... CARE!

    # Is it better with a generator or just returning a list (or dict by FK)?
    # we could even return a dictionary {id:object}, though it would not be
    # very coherent after the first level
    # objects = {}

    for row in rows:
        o = {}
        print "--New Row--"
        for i, col_name in enumerate(cols):
            try:
                app_table, column = col_name.split('__')
            except:
                app_table, column = '', col_name
            print app_table, column, row[i]

            e = o
            for k in _get_depth(alias_map, app_table):
                e = e.setdefault(k, {})
            e[column] = row[i]

        yield o
    return


    '''previous code, working only for 1 level and with no aliases'''

    # Django queries come as "app_model"."field" and I rename the resulting columns as "app_model__field", so that I don't have synonyms issues!
    # I expect the table name to have a space before - or, not a parenthesis - so that I do not rename aggregates and similar
    # @TODO this is a little weak as it is... but it's quick and work for our current needs.
    # To be throuly tested!
    query[0] = re.sub(r'\s"(\w*)"\."(\w*)"', r' "\1"."\2" AS "\1__\2"', query[0])
    query = 'FROM'.join(query)
    print "--- QUERY ---"
    print query
    print "-------------\n"

    cursor.execute(query)
    desc = cursor.description
    cols = [col[0] for col in desc]

    ## if we need to modify the dicts, that's where it's gonna happen:
    # But maybe in that case it's better /not/ to use the dictcursor, and rather take care of it ourselves.
    rows = cursor.fetchall()

    ### The following is potentially processing intensive if there are a lot of results... CARE!

    # Is it better with a generator or just returning a list (or dict by FK)?
    # objects = {}
    for row in rows:
        object = {}
        # if not row:
        #     return
        for i, col_name in enumerate(cols):
            try:
                app_table, column = col_name.split('__')
            except:
                app_table = main_table
                column = col_name
                ### this happens with aggregates for instance
            if app_table == main_table:
                object[column] = row[i]
            else:
#                app, table = app_table.split('_')
                app, table = app_table.rsplit('_', 1)
                object[table] = object.get(table, {})
                object[table][column] = row[i]
        #yield object



def prefetch_generic_fk_values(queryset):
    '''
    Inspired from
    https://gist.github.com/justinfx/3095246

    Cache the generic relation field of all the objects
    in the queryset, using larger bulk queries ahead of time.

    Improved from original by Daniel Roseman:
    http://blog.roseman.org.uk/2010/02/22/django-patterns-part-4-forwards-generic-relations/


    TO BE COMPARED WITH PREFETCH RELATED... when we get it to work!

    We produce 3 things:

    1. Enrich queryset with ._content_object_cache (subsequent calls to object still trigger
    2. A flat list of objects
    3. A list of members with attached the objects
    '''
    generics = {}
    print "Before going through qs", connection.queries
    for item in queryset:
        if item.object_id is not None:
            generics.setdefault(item.content_type_id, set()).add(item.object_id)

    print "After going through qs", connection.queries

    content_types = ContentType.objects.in_bulk(generics.keys())
    #
    ## content types have their own cache in django already - but when you access a few, the in_bulk still seem a better idea...?
    # content_types = ContentType.objects

    relations = {}
    items = []
    for ct_id, fk_list in generics.iteritems():
        # content_type = content_types.get_for_id(ct)
        content_type = content_types[ct_id]
        ct_model = content_type.model_class()
        # In the following, I trust each Model Manager to load its required related objects.
        # Though for objects I could also rely on a complex large in memory cache...
        # using a unique id made with content_type_id:object_id so that it's unique...
        # relations[ct] = ct_model.objects.in_bulk(list(fk_list))
        '''
        if hasattr(ct_model, 'objects_prefetch'):
            print "** {} has a prefetch manager!".format(ct_model)
            # relations[ct_id] = {o['id']: o for o in ct_model.objects_prefetch.filter(id__in=list(fk_list)).values()}
            relations[ct_id] = {o['id']: o for o in qs_iterator_values(ct_model.objects_prefetch.filter(id__in=list(fk_list)))}
        else:
            print "** {} has NO prefetch manager!".format(ct_model)
            relations[ct_id] = {o['id']: o for o in ct_model.objects.filter(id__in=list(fk_list)).values()}
        '''
        ##  Here I should check if the model has _meta related / prefetch attributes and use the correct
        # manager / queryset / etc.
        manager = getattr(ct_model, 'objects_overview', ct_model.objects)

        relations[ct_id] = {o['id']: o for o in queryset_as_dict(manager.filter(id__in=list(fk_list)))}

        for o in relations[ct_id].values():  # values of a dict, NOT of a QS!
            o['content_type'] = '.'.join([content_type.app_label, content_type.name])
            o['content_type_id'] = ct_id
            items.append(o)

    member_values = []
    for item in queryset.values()[:]:
        if item['object_id'] is not None:
            item['object'] = relations[item['content_type_id']][item['object_id']]
        member_values.append(item)

    for item in queryset:
        try:
            cached_val = relations[item.content_type_id][item.object_id]
        except KeyError:
            cached_val = None
        setattr(item, '_content_object_cache', cached_val)

    # or use the queryset with the prefilled "_content_object_cache"
    return items, member_values
    # flatten relations
    # return list(chain.from_iterable([r.values() for r in relations.values()]))

