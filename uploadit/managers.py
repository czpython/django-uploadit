from django.db import models

from uploadit.conf import settings
from uploadit.utils import callable_from_string

class FileManager(models.Manager):

    use_for_related_fields = True

    def get_custom_sorted(self, **kwargs):
        """
            Checks for a callable custom sorting.
            And returns its result.
            This does not necessarily return a queryset. It can return any type,
            it all depends on the return value of the custom sorting. In my case
            I had to implement natural sorting and could not find a way of doing it
            with a queryset so had to return a list.
        """
        qs = self.get_query_set().filter(**kwargs)
        ordering = callable_from_string(settings.UPLOADIT_FILE_SORTING)
        if callable(ordering):
            customsorted = ordering(qs)
            return customsorted
        return qs
