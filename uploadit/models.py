from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


def calc_img_path(instance, name):
	slug = instance.parent.pk
	return "%s/%s" % (slug, name)


class UploadedFile(models.Model):
	"""
		Represents an uploaded file in the db.
	"""

	file = models.ImageField(upload_to=calc_img_path)
	parent_type = models.ForeignKey(ContentType)
    parent_id = models.CharField(max_length=100)
	parent = generic.GenericForeignKey('parent_type', 'parent_id')

	def __unicode__(self):
		return "%s - %s" %(self.file.name, str(self.parent))
