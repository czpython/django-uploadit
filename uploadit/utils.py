import os
import logging

from django.contrib.contenttypes.models import ContentType


def get_object_from_ctype(ctype_id, pk):
    ctype = ContentType.objects.get(id=ctype_id)
    generic = ctype.get_object_for_this_type(pk=pk)
    return generic

def get_ctype(request, path):
    # Id of the content type object that represents the parent class
    ctype = request.POST.get('ctype')

    try:
        ctype = ContentType.objects.get(id=ctype)
    except ContentType.DoesNotExist, ValueError:
        try:
            ctype = ContentType.objects.get_by_natural_key(*path.split('.'))
        except ContentType.DoesNotExist:
            ctype = None

    # A unique value for the parent object.
    query = request.POST.get('pk')

    return ctype, query

def get_timestamp(datetime):
    return datetime.strftime("%Y%m%d%H%M%S%f")