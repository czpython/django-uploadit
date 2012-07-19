from django.db import models
from django.core.files import File

from uploadit.managers import FileManager
from uploadit.conf import settings
from uploadit.utils import callable_from_string


file_model = callable_from_string(settings.UPLOADIT_FILE_MODEL)


class UploadedFile(file_model):
    """
        Represents an uploaded file in the db.
    """

    objects = FileManager()

    class Meta:
        ordering = settings.UPLOADIT_OBJECTS_ORDERING


def process_file(**kwargs):
    """
        Default file processor.
    """
    filepath, filename = kwargs.pop('filepath'), kwargs.pop('filename')
    newargs = dict()
    for arg in kwargs:
        try: 
            UploadedFile._meta.get_field_by_name(arg)
            newargs[arg] = kwargs[arg]
        except models.FieldDoesNotExist:
            pass
    with File(open(filepath), name=filename) as f:
        UploadedFile.objects.create(file=f, **newargs)
    return
