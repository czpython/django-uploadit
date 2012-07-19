import mimetypes

from django.db import models


class DefaultUploadedFile(models.Model):
    """
        Defines a default class to extend UploadedFile.
    """

    file = models.FileField(upload_to='uploaded-files')
    upload_date = models.DateTimeField(auto_now_add=True)
    content_type = models.CharField(editable=False, max_length=100)

    class Meta:
        abstract = True

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
        super(DefaultUploadedFile, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.file.name