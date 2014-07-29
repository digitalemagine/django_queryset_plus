from django.db import models
from queryset_plus.managers import DetailsManager, OverviewManager

# Create your models here.


class SmartRelatedModel(models.Model):

    objects_details = DetailsManager()
    objects_overview = OverviewManager()

    class Meta:
        abstract = True
