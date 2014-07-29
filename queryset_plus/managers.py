
from django.db import connection, connections
from django.db import models


import django.db.models.options as options

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('related_modelfields', )


class SmartRelatedManager(models.Manager):

    def __init__(self, *args, **kwargs):
        super(SmartRelatedManager, self).__init__(*args, **kwargs)
        self._select_related = None
        self._prefetch_related = None

    def init(self, dict_name):
        # ._meta.concrete_fields]
        # print self.model._meta.related_modelfields

        if self._select_related is None or self._prefetch_related is None:
            self._select_related = set()
            self._prefetch_related = set()
            for modelfield_name in getattr(self.model._meta, 'related_modelfields', {dict_name:[]})[dict_name]:
                # here I should split by '__' and try to understand if it's:
                # a model, or a field of a related model. Only last /can/ be a field, but doesn't have to
                # I will trust Django to build correctly subsequent queries,
                # but a FK->M2M relation requires first a select_related then a prefetch_related so will not work out of the box with this system.
                # Ideally, use this kind of manager everywhere and re-set recursevely single level relations
                '''
                Otherwise, a possible logic would be to (recursevely) browse all elements of the split; as long
                '''
                field_name = modelfield_name.split('__')[0]
                # also, get_field_by_name might not be optimal http://django-model-internals-reference.readthedocs.org/en/latest/get_field_by_name.html
                # Is it better to use get_field or other?! GFbN builds a cache, so after all might be optimal.
                # get_field_by_name returns: (field_object, model, direct, m2m)  BUT it does not follow '__' relations
                (field, model, direct, m2m) = self.model._meta.get_field_by_name(field_name)
                if isinstance(field, models.ForeignKey):
                #if ???:  # unluckily there's no such a property... FK are direct as well as normal fields
                    self._select_related.add(field_name)
                    ## print "{} is a FK".format(field_name)
                elif isinstance(field, models.ManyToManyField):
                #elif m2m:
                    self._prefetch_related.add(field_name)
                    ## print "{} is a M2M".format(field_name)
                else:
                    raise Exception("Overview Manager: '{}'' is unknown: {}".format(field_name, field))

    def get_queryset(self):
        self.init()  # I have to init here, since in __init__ I don't seem to have access to the model yet...
        #return super(SmartRelatedManager, self).get_queryset()
        '''
        # join related and prefetched queryset results
        # related =
        # prefetched =
        '''
        qs = super(SmartRelatedManager, self).get_queryset().select_related(*self._select_related).prefetch_related(*self._prefetch_related)
        qs._select_related = self._select_related
        qs._prefetch_related = self._prefetch_related
        # print qs, qs._select_related
        return qs

    def as_dict(self, queryset):

        self.init()
        related = queryset.select_related(*self._select_related).values()

        prefetched = queryset.select_related(*self._select_related).prefetch_related(*self._prefetch_related).values()

        return related, prefetched
        # This is what really matters for our needs.
        #
        # Take ANY initial queryset? Probably possible in django 1.7 not here.
        related = self.get_queryset().select_related(*self._select_related).values()
        prefetched = []
        qs = self.get_queryset().select_related(*self._select_related).prefetch_related(*self._prefetch_related)
        print qs.values()
        prefetched = qs.values()
        # for m2m in self._prefetch_related:
        #    qs = self.get_queryset().select_related(*self._select_related).prefetch_related(*self._prefetch_related)
        print "---------Related:----------"
        print list(related)
        print "---------Prefetched:----------"
        print list(prefetched)
        return list(related) + list(prefetched)



class OverviewManager(SmartRelatedManager):

    def init(self):
        super(OverviewManager, self).init('overview')

    def get_queryset(self):
        return super(OverviewManager, self).get_queryset()


class DetailsManager(SmartRelatedManager):

    def init(self):
        super(DetailsManager, self).init('details')

    def get_queryset(self):
        return super(DetailsManager, self).get_queryset()
