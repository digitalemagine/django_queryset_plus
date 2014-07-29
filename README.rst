======================
Django queryset_values
======================

Very simple package that tries to improve django queryset.
In particular, conversion to dict (queryset.values()) is currently very limited
when the query includes related or prefetch fields.

Django QuerySet.values() issues
===============================

The important things to remember are:

* Django cannot produce .values() for select_related (even less prefetch_related) - see https://code.djangoproject.com/ticket/3358
* prefetch_related require additional DB requests and are only executed when a QS is evaluated
* the SQL resulting from `select_related(foreignkey_model)` and  `select_related(foreignkey_model__field1, foreignkey_model__field2)` is the SAME! Django select_related always query the database for ALL columns. Then filters them out in the 'values()' function.


Alternative options (more precise comments for these should be added)


.. _in_bulk: http://https://docs.djangoproject.com/en/1.6/ref/models/querysets/#in-bulk
.. _django_serializers: https://docs.djangoproject.com/en/1.6/topics/serialization/

* `in_bulk`_
* `model_to_dict` (django.forms.models.model_to_dict)

    - ``editable=False`` fields are automatically ignored in model_to_dict
* django_serializers_

.. code-block:: python

    from django.core import serializers
    data = serializers.serialize('python', DictModel.objects.all())

Django Queryset Query obj (<django.db.models.sql.query.Query>)
==============================================================

The `queryset.query` object is the one that performs the real magic,
transforming a queryset series of filters/related/etc. into some real SQL.

In the following, we will use the test_app models to make concrete examples

Query Properties
----------------

It holds three important properties for us - ONCE IT HAS BEEN COMPILED -:

related_fields
    a dictionary-tree of the related fields,
    eg.:

.. code-block:: python

    {
        'a': {},
        'c': {
            'b': {
                'a': {}
                }
            }
    }


alias_map
    a dictionary of table-aliases -> JoinInfo details

    if a table is aliased, the key will be its aliased name. The value is a named tuple, `JoinInfo`, that contains:

.. code-block:: python

    test_app_modeld:
        JoinInfo(table_name=u'test_app_modeld', rhs_alias=u'test_app_modeld', join_type=None, lhs_alias=None, join_cols=((None, None),), nullable=False, join_field=None)
    T5 :
        JoinInfo(table_name=u'test_app_modela', rhs_alias='T5', join_type='INNER JOIN', lhs_alias=u'test_app_modelb', join_cols=(('a_id', u'id'),), nullable=False, join_field=<django.db.models.fields.related.ForeignKey: a>)
    test_app_modela :
        JoinInfo(table_name=u'test_app_modela', rhs_alias=u'test_app_modela', join_type='INNER JOIN', lhs_alias=u'test_app_modeld', join_cols=(('a_id', u'id'),), nullable=False, join_field=<django.db.models.fields.related.ForeignKey: a>)
    test_app_modelc :
        JoinInfo(table_name=u'test_app_modelc', rhs_alias=u'test_app_modelc', join_type='INNER JOIN', lhs_alias=u'test_app_modeld', join_cols=(('c_id', u'id'),), nullable=False, join_field=<django.db.models.fields.related.ForeignKey: c>)
    test_app_modelb :
        JoinInfo(table_name=u'test_app_modelb', rhs_alias=u'test_app_modelb', join_type='INNER JOIN', lhs_alias=u'test_app_modelc', join_cols=(('b_id', u'id'),), nullable=False, join_field=<django.db.models.fields.related.ForeignKey: b>)


join_map
    a dictionary mapping
    (I do not know why the values of the dict are also a tuple - in which case there's more than one table?)

 .. code-block:: python

    # tuples structure

    (from_model_table, to_model_table, (join_field_from, join_field_to)): (to_model_table_alias,)

 .. code-block:: python

    # full-example

    (None, u'test_app_modeld', None) :
      (u'test_app_modeld',)
    (u'test_app_modeld', u'test_app_modela', (('a_id', u'id'),)) :
      (u'test_app_modela',)
    (u'test_app_modeld', u'test_app_modelc', (('c_id', u'id'),)) :
      (u'test_app_modelc',)
    (u'test_app_modelc', u'test_app_modelb', (('b_id', u'id'),)) :
      (u'test_app_modelb',)
    (u'test_app_modelb', u'test_app_modela', (('a_id', u'id'),)) :
      ('T5',)

    # indented for clarity

    D: (None, u'test_app_modeld', None) :
        (u'test_app_modeld',)
        A: (u'test_app_modeld', u'test_app_modela', (('a_id', u'id'),)) :
            (u'test_app_modela',)
        C: (u'test_app_modeld', u'test_app_modelc', (('c_id', u'id'),)) :
            (u'test_app_modelc',)
            B: (u'test_app_modelc', u'test_app_modelb', (('b_id', u'id'),)) :
                (u'test_app_modelb',)
                A: (u'test_app_modelb', u'test_app_modela', (('a_id', u'id'),)) :
                    ('T5',)

Query Execution
---------------

but from the django sql we are getting

.. code-block::

    table_d.fields
    table_a.fields
    table_c.fields
    table_b.fields
    alias_ta.fields

in this particular example (indentation is added for clarity):

.. code-block:: sql

    SELECT
        "test_app_modeld"."id", "test_app_modeld"."d1", "test_app_modeld"."d2", "test_app_modeld"."a_id", "test_app_modeld"."c_id",
            "test_app_modela"."id", "test_app_modela"."a1", "test_app_modela"."a2",
            "test_app_modelc"."id", "test_app_modelc"."c1", "test_app_modelc"."c2", "test_app_modelc"."b_id",
                "test_app_modelb"."id", "test_app_modelb"."b1", "test_app_modelb"."b2", "test_app_modelb"."a_id",
                    T5."id", T5."a1", T5."a2"
    FROM "test_app_modeld"
        INNER JOIN "test_app_modela" ON ( "test_app_modeld"."a_id" = "test_app_modela"."id" )
        INNER JOIN "test_app_modelc" ON ( "test_app_modeld"."c_id" = "test_app_modelc"."id" )
        INNER JOIN "test_app_modelb" ON ( "test_app_modelc"."b_id" = "test_app_modelb"."id" )
        INNER JOIN "test_app_modela" T5 ON ( "test_app_modelb"."a_id" = T5."id" )

resulting in:
(the following has been pre-processed to alias /all/ column so that
we can retrieve the tablename and the field name. Hereby we list:
(table, field, value))

.. code-block::

    test_app_modeld id 1
    test_app_modeld d1 1
    test_app_modeld d2 modelD#1
    test_app_modeld a_id 3
    test_app_modeld c_id 1
    test_app_modela id 3
    test_app_modela a1 3
    test_app_modela a2 modelA#3
    test_app_modelc id 1
    test_app_modelc c1 1
    test_app_modelc c2 modelC#1
    test_app_modelc b_id 1
    test_app_modelb id 1
    test_app_modelb b1 1
    test_app_modelb b2 modelB#1
    test_app_modelb a_id 1
    T5 id 1
    T5 a1 1
    T5 a2 modelA#1


working with prefetch_related
-----------------------------

An important optimization beside the related fields are prefetch fields.
(Django model/queryset classes are lazy and will perform additional db requests
for anything that hasn't been obtained yet).

See prefetch_related code and try to copy its logic into our 'qs_to_dict' one.


queryset_as_dict(): Building a dictionary tree
==============================================

Expected result

from the query we obtain a flat list of columns without a structure
- and a potential loss in table names due to aliases - that we have to map to
a tree structure equivalent to that of the related_fields.

Eg. for our test example:

.. code-block::

    instance_d.fields
              .a = instance_a.fields
              .c = instance_c.fields
                             .b = instance_b.fields
                                            .a = instance_a.fields

thus:

.. code-block::

    # instance of ModelD:
    {
        d1: value,
        d2: value,
        a: {
            a1: value,
            a2: value,
        }
        c: {
            c1: value,
            c2: value,
            b: {
                b1: value,
                b2: value,
                a: {
                    a1: value,
                    a2: value,
                }
            }
        }
    }

to make this example clearer, let's add some ids (we are talking about DB
rows after all!) that will help us identify precisely the relations:

.. code-block:: json

    {
        "id": 0,
        "d1": "d1",
        "d2": "d2",
        "a": {
            "id": 3,
            "a1": "d#0:a#3:a1",
            "a2": "d#0:a#3:a2",
        },
        "c": {
            "id": 4,
            "c1": "d#0:c#4:c1",
            "c2": "d#0:c#4:c2",
            "b": {
                "id": 5,
                "b1": "d#0:c#4:b#5:b1",
                "b2": "d#0:c#4:b#5:b2",
                "a": {
                    "id": 8,
                    "a1": "d#0:c#4:b#5:a#8:a1",
                    "a2": "d#0:c#4:b#5:a#8:a2",
                }
            }
        }
    }


The `_get_depth()` function takes care of mapping the alias table name to the
correct tree leaf.



Using with Django-Rest-Framework
================================

How does this correctly integrates with both (Model)Viewsets, Views (*ModelView, *APIView),
and (Model)Serializer?

There are several places where we might want to integrate:

1. Serializers
--------------

IDEA:
The serializer should just do nothing but retrieve the dict

create your serializer using queryset_plus.rest_framework.ModelSerializer

Specify the fields you want to retrieve.
That will be transformed into a `related_fields().prefetch_fields()` combo

    class MyModelSerializer(queryset_plus.rest_framework.ModelSerializer):
        class Meta:
            model = Snippet  # gets the queryset
            fields = ('id', 'title', 'author')  # can span FKs or M2M -> builds the queryset
            # coming from QuerySet makes more sense because Related and Prefetch can be
            # more precisely specified


Internally, `queryset_plus.rest_framework.ModelSerializer`
will build a QuerySet and call queryset_as_dict on it instead of using the real
rest_framework.serializers.ModelSerializer.

2. ModelViewSets
----------------

Using directly a queryset_plus.rest_framework.ModelViewsets might automatically
do everything using a default Serializer that does nothing - or even without a serializer?

We do this by editing the mixins.

Reading only. Write still requires going through all of the models.

3. GenericViews
---------------

to do


Testing django-queryset-plus
============================

In django >= 1.6 it's not possible to have model definition only for tests, see:
https://code.djangoproject.com/ticket/7835

Some solutions are provided here:
http://stackoverflow.com/questions/502916/django-how-to-create-a-model-dynamically-just-for-testing

Instead, I find it cleaner and nicer to have a very simple included minimal project;
thus to test the queryset-plus library please jump into queryset_plus_test and run

$ ./manage.py test queryset_plus.tests
