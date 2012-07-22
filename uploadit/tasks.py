from os import unlink as delete_file

from celery.task import Task
from celery import registry, group

from uploadit.utils import callable_from_string
from uploadit.conf import settings
from uploadit.models import UploadedFile



UPLOADIT_PROCESS_FILE = callable_from_string(settings.UPLOADIT_PROCESS_FILE)


class UploaditFileUpload(Task):
    """ This task is in charge of uploading the file to the proper location in media
        and creating the db objects.
        This task can be called by a single image upload( uploadit.views.upload_image ),
        or a multiple image upload ( uploadit.utils.upload_images ).
        Beware that if calling this task from uploadit.views.upload_image, the image is a tmp file created
        by django's TemporaryFileUploadHandler which gives the image a random name, so you will lose the original name.
    """
    name = "uploadit.tasks.upload_file"
    ignore_result = True

    def run(self, filepath, filename, **kwargs):
        """
            @filepath: Path to the temporary uploaded file.
            @filename - Original name of the file.
        """
        logger = self.get_logger()

        # Before we go any further, first verify that the file actually exists.
        try:
            with open(filepath) as f: pass
        except IOError:
            logger.error("Couldn't find file to upload, tried %s" % filepath)
            return None
        else:
            kwargs.update({'filepath': filepath, 'filename': filename}, countdown=0)
            UPLOADIT_PROCESS_FILE(**kwargs)
        # Remove tmp file :)
        delete_file(filepath)
        return

task_upload_file = registry.tasks[UploaditFileUpload.name]
