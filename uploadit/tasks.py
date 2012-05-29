import os
import logging
from datetime import datetime

from django.core.files.images import ImageFile
from django.contrib.contenttypes.models import ContentType

from celery import registry
from celery.task import Task

from uploadit.utils import get_object_from_ctype
from uploadit.models import UploadedFile


class UploaditFileUpload(Task):
    name = "uploadit.tasks.upload_file"
    ignore_result = True

    def run(self, pk, parenttmpdir, imgname, ctype_id):
        """
            pk - The pk of the parent object.
            parenttmpdir - The path to the temporary parent object
        """

        # Absolute path
        filepath = os.path.join(parenttmpdir, imgname)
        try:
            img = ImageFile(open(filepath, 'rb'))
        except IOError:
            logging.error("Couldn't find file to upload, tried %s" % filepath)
            return
        parent = get_object_from_ctype(ctype_id, pk)
        file_ = UploadedFile.objects.create(parent=parent)
        file_.file.save(path, img, save=True)
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
        try:
            image = ImageFile(open(filepath))
        except IOError:
            logging.error("Can't find django created tmp file at %s" % filepath)
            return

        tmpfilename = datetime.now().strftime("%Y%m%d%H%M%S%f") + original
        # Path to temporary image file, unfortunately i have no way of getting the extension 
        # of the file. So the temp files are being saved without an extension.
        tmpfile = os.path.join(parentpath, tmpfilename)
        try:
            tmp = open(tmpfile, 'w')
        except IOError:
            logging.error("Can't create tmp file %s" % tmpfile)
            return
        for chunk in image.chunks():
            tmp.write(chunk)
            tmp.flush()
        return

task_upload_file = registry.tasks[UploaditFileUpload.name]
task_process_file = registry.tasks[UploaditFileProcess.name]
