from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

try:
    # This setting allows third party apps to change the order the files are retrieved.
    UPLOADIT_OBJECTS_ORDERING = settings.UPLOADIT_OBJECTS_ORDERING
except AttributeError:
    UPLOADIT_OBJECTS_ORDERING = ['id',]


def calc_file_path(instance, name):
    folder = instance.parent.pk
    return "%s/%s" % (folder, name)


class UploadedFile(models.Model):
    """
        Represents an uploaded file in the db.
    """

    file = models.ImageField(upload_to=calc_file_path)
    parent_type = models.ForeignKey(ContentType)
    parent_id = models.CharField(max_length=100)
    parent = generic.GenericForeignKey('parent_type', 'parent_id')

    def __unicode__(self):
        return "%s - %s" %(self.file.name, str(self.parent))

    class Meta:
        ordering = UPLOADIT_OBJECTS_ORDERING
