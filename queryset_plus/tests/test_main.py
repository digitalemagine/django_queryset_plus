from django.test import TestCase


from django.conf import settings
from django.core.management import call_command
from django.db.models.loading import load_app

from django.core import serializers
from django.forms.models import model_to_dict

from test_project.test_app.models import *

from queryset_plus.db import queryset_as_dict

import json


'''
Gotchas:

Since django 1.6 there's no easy way to create models only for a test...

Thus... activate them in the models.py!

'''

class DjangoQuerySetPlusTestCase(TestCase):


    def setUp(self):

        MAX = 4

        model_a_values = []
        for a in range(1, MAX):
            a1 = a
            a2 = "modelA#{}".format(a)
            ModelA.objects.create(a1=a1, a2=a2)
            # expected results:
            model_a_values.append({
                "a1": a1,
                "a2": a2,
            })

        model_b_values = []
        for b in range(1, MAX):
            b1 = b
            b2 = "modelB#{}".format(b)
            ModelB.objects.create(b1=b1, b2=b2, a=ModelA.objects.all()[b-1])

            # expected results:
            model_b_values.append({
                "b1": b1,
                "b2": b2,
                "a": model_a_values[b-1]
            })

        model_c_values = []
        for c in range(1, MAX):
            c1 = c
            c2 = "modelC#{}".format(c)
            ModelC.objects.create(c1=c1, c2=c2,
                b=ModelB.objects.all()[c-1]
            )

            # expected results:
            model_c_values.append({
                "c1": c1,
                "c2": c2,
                "b": model_b_values[c-1],
            })

        model_d_values = []
        for d in range(1, MAX):
            d1 = d
            d2 = "modelD#{}".format(d)
            ModelD.objects.create(d1=d1, d2=d2,
                a=ModelA.objects.all()[MAX-1-d],
                c=ModelC.objects.all()[d-1]
            )

            # expected results:
            model_d_values.append({
                "d1": d1,
                "d2": d2,
                "a": model_a_values[MAX-1-d],
                "c": model_c_values[d-1],
            })


        self.model_a_values = model_a_values
        self.model_b_values = model_b_values
        self.model_c_values = model_c_values
        self.model_d_values = model_d_values


    def test_queryset_as_dict(self):
        """Prints dicts out of queryset correctly..."""
        """
        The best way to test would be to serialize the models using django
        (and thus it's form facilities):
        django.forms.models.model_to_dict

        Or maybe to compare really everything!

        """


#        self.assertEqual(lion.speak(), 'The lion says "roar"')
#        self.assertEqual(cat.speak(), 'The cat says "meow"')


        qs = ModelD.objects.all().select_related('a', 'c', 'c__b', 'c__b__a')
        print "expected", json.dumps(self.model_d_values, indent=4, sort_keys=True)
        print json.dumps(list(queryset_as_dict(qs)), indent=4, sort_keys=True)

        return

        for qs in [
            #ModelC.objects.all().select_related('b__a'),
            ModelD.objects.all().select_related('a', 'c', 'c__b', 'c__b__a'),
        ]:
            ## These are the things we can compare:
            # print "queryset", qs
            # print "django.serializers", serializers.serialize('python', qs)
            # print "model_to_dict", [model_to_dict(instance) for instance in qs]
            result = list(queryset_as_dict(qs))
            print "----"
            print "queryset_as_dict:\n\n", result
            print "----"


