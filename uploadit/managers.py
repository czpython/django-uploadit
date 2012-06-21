from django.db import models
from django.contrib.contenttypes.models import ContentType

from uploadit.conf import settings


class FileManager(models.Manager):
    def ordered(self, parent):
        parent_type = ContentType.objects.get_for_model(parent.__class__)
        qs = self.get_query_set().filter(parent_type=parent_type.id, parent_id=parent.pk)
        ordering = settings.get_ordering()
        if callable(ordering):
            results = ordering(qs)
        else:
            results = qs.filter(*settings.UPLOADIT_OBJECTS_ORDERING)
        return results
