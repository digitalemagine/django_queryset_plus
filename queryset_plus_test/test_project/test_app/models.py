from django.db import models


# Test Models!

class ModelA(models.Model):

    a1 = models.IntegerField()
    a2 = models.CharField(max_length=255)


class ModelB(models.Model):

    b1 = models.IntegerField()
    b2 = models.CharField(max_length=255)

    a = models.ForeignKey(ModelA)


class ModelC(models.Model):

    c1 = models.IntegerField()
    c2 = models.CharField(max_length=255)

    b = models.ForeignKey(ModelB)


class ModelD(models.Model):

    d1 = models.IntegerField()
    d2 = models.CharField(max_length=255)

    a = models.ForeignKey(ModelA)
    c = models.ForeignKey(ModelC)

