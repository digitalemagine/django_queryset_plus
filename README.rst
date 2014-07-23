======================
Django queryset_values
======================

Very simple package that tries to provide queryset to dict (values) functions missing from Django.

Django QuerySet issues
======================

The important things to remember are:

* Django cannot produce .values() for select_related (even less prefetch_related) - see https://code.djangoproject.com/ticket/3358
* prefetch_related require additional DB requests and are only executed when a QS is evaluated
* the SQL resulting from `select_related(foreignkey_model)` and  `select_related(foreignkey_model__field1, foreignkey_model__field2)` is the SAME! Django select_related always query the database for ALL columns. Then filters them out in the 'values()' function.


Alternative options (more precise comments for these should be added)


* `in_bulk`
* `model_to_dict` (django.forms.models.model_to_dict)
 - editable=False fields are automatically ignored in model_to_dict
* django serializers
```
from django.core import serializers
data = serializers.serialize('python', DictModel.objects.all())
```

Django Queryset Query obj (<django.db.models.sql.query.Query>)
==============================================================

The `queryset.query` object is the one that performs the real magic,
transforming a queryset series of filters/related/etc. into some real SQL.

In the following, we will use the test_app models to make concrete examples

It holds three important properties for us - ONCE IT HAS BEEN COMPILED -:

related_fields
    a dictionary-tree, eg:

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

    ::
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

    (i do not know what the value is a tuple - in which case there's more than one table?)

    >   (from_model_table, to_model_table, (join_field_from, join_field_to)):
            (to_model_table,)

    >   (u'test_app_modeld', u'test_app_modela', (('a_id', u'id'),)) :
    >     (u'test_app_modela',)
    >   (u'test_app_modeld', u'test_app_modelc', (('c_id', u'id'),)) :
    >     (u'test_app_modelc',)
    >   (None, u'test_app_modeld', None) :
    >     (u'test_app_modeld',)
    >   (u'test_app_modelb', u'test_app_modela', (('a_id', u'id'),)) :
    >     ('T5',)
    >   (u'test_app_modelc', u'test_app_modelb', (('b_id', u'id'),)) :
    >     (u'test_app_modelb',)






Testing django-queryset-plus
============================

In django >= 1.6 it's not possible to have model definition only for tests, see:
https://code.djangoproject.com/ticket/7835

Some solutions are provided here:
http://stackoverflow.com/questions/502916/django-how-to-create-a-model-dynamically-just-for-testing

Instead, I find it cleaner and nicer to have a very simple included minimal project;
thus to test the queryset-plus library please jump into queryset_plus_test and run

$ ./manage.py test queryset_plus.tests
