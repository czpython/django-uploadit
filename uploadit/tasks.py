from os import unlink as delete_file

from django.core.files import File

from celery.task import Task
from celery import registry, group

from uploadit.models import FileGroup, UploadedFile


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

    def run(self, filepath, filename, filecount=None, group=None):
        """
            @filepath: Path to the temporary uploaded file.
            @filename - Original name of the file.
            @group - Unique group name, to use for grouping this file.
        """
        logger = self.get_logger()

        try:
            file_ = File(open(filepath), name=filename)
        except IOError:
            logger.error("Couldn't find file to upload, tried %s" % filepath)
            return None
        uploaded_file = UploadedFile(file=file_)
        if group:
            fgroup = FileGroup.objects.get_or_create(identifier=group, defaults={})[0]
            fgroup.files.add(uploaded_file)
         # Remove tmp file :)
        delete_file(filepath)
        return

task_upload_file = registry.tasks[UploaditFileUpload.name]
