from django.conf import settings

# This setting allows third party apps to change the order the files are retrieved.
UPLOADIT_OBJECTS_ORDERING = getattr(settings, 'UPLOADIT_OBJECTS_ORDERING', ['id',])

# Allows for last minute custom sorting of files.
UPLOADIT_FILE_SORTING = getattr(settings, 'UPLOADIT_FILE_SORTING', None)

# Path to the directory where all temporary files will be uploaded to.
# The reason for this settings is because I don't use Django's TemporaryFileUploadHandler
UPLOADIT_TEMP_DIR = getattr(settings, 'UPLOADIT_TEMP_DIR', None) or getattr(settings, 'FILE_UPLOAD_TEMP_DIR', None) or settings.PROJECT_ROOT
