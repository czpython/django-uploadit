import mimetypes

from django.db import models

from uploadit.conf import settings
from uploadit.managers import FileManager


def calc_file_path(instance, name):
    if not instance.group is None:
        return "%s/%s" % (instance.group.identifier, name)
    return "uploaded-files/%s" % name


class FileGroup(models.Model):
    """
        A group of files.
        Usefull for Image Galleries.
    """

    identifier = models.CharField(max_length=200, unique=True)


    def __unicode__(self):
        return self.identifier

    def get_files(self):
        return self.files.get_custom_sorted()


class UploadedFile(models.Model):
    """
        Represents an uploaded file in the db.
    """

    file = models.FileField(upload_to=calc_file_path)
    content_type = models.CharField(editable=False, max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)
    group =  models.ForeignKey(FileGroup, null=True, blank=True, related_name="files")
    objects = FileManager()

    class Meta:
        ordering = settings.UPLOADIT_OBJECTS_ORDERING


    def is_image(self):
        if self.content_type == "image":
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        (mime_type, encoding) = mimetypes.guess_type(self.file.url)
        try:
            self.content_type = mime_type.split("/")[0]
        except:
            self.content_type = "text"
        super(UploadedFile, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.file.name

