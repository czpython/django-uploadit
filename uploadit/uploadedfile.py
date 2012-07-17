from os.path import join as join_path

from django.core.files.uploadedfile import UploadedFile

from uploadit.conf import settings

UPLOADIT_TEMP_DIR = settings.UPLOADIT_TEMP_DIR


class InDiskUploadedFile(UploadedFile):
    """
    A regular file uploaded to disk.
    """
    def __init__(self, name, content_type, size, charset):
        file = open(join_path(UPLOADIT_TEMP_DIR, name), 'w')
        super(InDiskUploadedFile, self).__init__(file, name, content_type, size, charset)

    def file_path(self):
        """
        Returns the full path of this file.
        """
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except OSError as e:
            # File was already removed...
            return