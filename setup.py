#!/usr/bin/env python

from setuptools import setup

setup(
    name="django-uploadit",
    version="0.0.1",
    description="A Multifile uploader for Django.",
    author="Paulo Alvarado",
    author_email="commonzenpython@gmail.com",
    url="http://github.com/czpython/django-uploadit",
    packages=['uploadit'],
    install_requires=[
        'django-celery',
    ],
)