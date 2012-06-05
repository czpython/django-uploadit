import os
from datetime import datetime

from django.core.files.images import ImageFile
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from celery import registry
from celery.task import Task
# Celery 2.5.x compatibility
try:
    from celery import group
except ImportError:
    from celery.task.sets import TaskSet as group

from uploadit.utils import get_object_from_ctype, get_timestamp
from uploadit.models import UploadedFile


SEPARATOR = settings.SECRET_KEY

def upload_images(parent, datetimefield, tmpdir):
    """
        Main function, in charge of uploading all images as not tmp.
        And saves the proper db objects.
        This function NEEDS to be called to complete every upload batch.
    """
    ctype = ContentType.objects.get_for_model(parent)

    tmpfoldername = get_timestamp(datetimefield) + parent.pk

    parenttmpdir = os.path.join(tmpdir, tmpfoldername)

    logger = Task.get_logger()

    try:
        files = os.listdir(parenttmpdir)
    except OSError:
        logger.error("Couldn't find parent tmp folder, tried %s" % parenttmpdir)
        return
    else:
        job = group([task_upload_file.subtask((parent.pk, os.path.join(parenttmpdir, fil), ctype.id, fil)) for fil in files])
        result = job.apply_async()
        result.save()
    return result


class UploaditFileUpload(Task):
    """ This task is in charge of uploading the file to the proper location in media
        and creating the db objects.
        This task can be called by a single image upload( uploadit.views.upload_image ),
        or a multiple image upload ( uploadit.utils.upload_images ).
        Beware that if calling this task from uploadit.views.upload_image, the image is a tmp file created
        by django's TemporaryFileUploadHandler which gives the image a random name, so you will lose the original name.
    """
    name = "uploadit.tasks.upload_file"
    ignore_result = False

    def run(self, pk, filepath, ctype_id, original=None):
        """
            pk - The primary key of the parent object.
            filepath - Absolute path to tmp file.
            ctype_id - Content Type Id of the parent model.
            original - Original name of file.
        """
        logger = self.get_logger()

        try:
            img = ImageFile(open(filepath, 'rb'))
        except IOError:
            logger.error("Couldn't find file to upload, tried %s" % filepath)
            return
        parent = get_object_from_ctype(ctype_id, pk)
        original = original or img.name
        file_ = UploadedFile.objects.create(parent=parent)
        original = original.split(SEPARATOR)[1]
        file_.file.save(original, img, save=True)
        # Remove tmp file :)
        os.unlink(filepath)
        return

class UploaditFileProcess(Task):
    """
        This task is in charge of creating the tmp file.
    """
    name = "uploadit.tasks.process_file"
    ignore_result = True

    def run(self, parentpath, filepath, original):
        """
            parentpath - The path where all tmp files for this parent are being stored.
            filepath - The path to the uploaded temporary image file.
            original - Original file name.
        """

        logger = self.get_logger()
        try:
            image = ImageFile(open(filepath))
        except IOError:
            logger.error("Can't find django created tmp file at %s" % filepath)
            return

        tmpfilename = datetime.now().strftime("%Y%m%d%H%M%S%f") + SEPARATOR + original
        # Path to temporary image file, unfortunately i have no way of getting the extension 
        # of the file. So the temp files are being saved without an extension.
        tmpfile = os.path.join(parentpath, tmpfilename) 
        try:
            tmp = open(tmpfile, 'w')
        except IOError:
            logger.error("Can't create tmp file %s" % tmpfile)
            return
        for chunk in image.chunks():
            tmp.write(chunk)
            tmp.flush()
        return

task_upload_file = registry.tasks[UploaditFileUpload.name]
task_process_file = registry.tasks[UploaditFileProcess.name]
