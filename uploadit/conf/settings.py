import os
import sys

from django.conf import settings


try:
	UPLOADIT_PARENT_CLASS = settings.UPLOADIT_PARENT_CLASS
except AttributeError:
	raise ImproperlyConfigured('Please define UPLOADIT_PARENT_CLASS in your settings.')

try:
	UPLOADIT_PARENT_DATETIME = settings.UPLOADIT_PARENT_DATETIME
except AttributeError:
	raise ImproperlyConfigured('Please define UPLOADIT_PARENT_DATETIME in your settings.')

# This setting allows third party apps to change the order the files are retrieved.
UPLOADIT_OBJECTS_ORDERING = getattr(settings, 'UPLOADIT_OBJECTS_ORDERING', ['id',])

UPLOADIT_TEMP_FILES = getattr(settings, 'UPLOADIT_TEMP_FILES', os.path.join(os.environ.get('VIRTUAL_ENV'), sys.prefix))
UPLOADIT_SEPARATOR = getattr(settings, 'UPLOADIT_SEPARATOR', settings.SECRET_KEY)

# Allows for last minute custom sorting for the images in a gallery.
UPLOADIT_FILE_SORTING = getattr(settings, 'UPLOADIT_FILE_SORTING', None)


def _callable_from_string(string_or_callable):
    """
        Thanks to https://github.com/mbi/django-simple-captcha/blob/master/captcha/conf/settings.py#L31
        for this snippet.
    """
    if string_or_callable is None:
    	return
    elif callable(string_or_callable):
        return string_or_callable
    else:
        return getattr(__import__('.'.join(string_or_callable.split('.')[:-1]), {}, {}, ['']), string_or_callable.split('.')[-1])


def get_ordering():
	if UPLOADIT_FILE_SORTING:
		return _callable_from_string(UPLOADIT_FILE_SORTING)
	else:
		return UPLOADIT_OBJECTS_ORDERING