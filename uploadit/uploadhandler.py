from django.core.files.uploadhandler import FileUploadHandler

from uploadit.uploadedfile import InDiskUploadedFile



class UploaditFileUploadHandler(FileUploadHandler):
    """
        An exact replica of TemporaryUploadedFile, but instead of creating tmp files,
        it creates regular files.
    """
    def __init__(self, *args, **kwargs):
        super(UploaditFileUploadHandler, self).__init__(*args, **kwargs)

    def new_file(self, file_name, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super(UploaditFileUploadHandler, self).new_file(file_name, *args, **kwargs)
        self.file = InDiskUploadedFile(self.file_name, self.content_type, 0, self.charset)

    def receive_data_chunk(self, raw_data, start):
        self.file.write(raw_data)

    def file_complete(self, file_size):
        self.file.seek(0)
        self.file.size = file_size
        return self.file