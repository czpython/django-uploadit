import os
import ipdb
from datetime import datetime


from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.conf import settings

# Celery 2.5.x compatibility
try:
    from celery import group
except ImportError:
    from celery.task.sets import TaskSet as group

from uploadit.tasks import task_upload_file, task_process_file
from uploadit.utils import get_ctype, get_timestamp

UPLOADIT_TEMP_FILES = settings.UPLOADIT_TEMP_FILES
# Path to the parent class containing the 
UPLOADIT_PARENT_CLASS = settings.UPLOADIT_PARENT_CLASS
UPLOADIT_PARENT_DATETIME = settings.UPLOADIT_PARENT_DATETIME

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"


@csrf_exempt
def upload_images(request):
    data = {'success': '0'}
    if request.method == "POST":
        ctype, pk = get_ctype(request, UPLOADIT_PARENT_CLASS)
        parent = ctype.get_object_for_this_type(pk=pk)
        tmpfoldername = get_timestamp(getattr(parent, UPLOADIT_PARENT_DATETIME)) + pk
        parenttmpdir = os.path.join(UPLOADIT_TEMP_FILES, tmpfoldername)
        try:
            files = os.listdir(parenttmpdir)
        except OSError:
            pass
        job = group([task_upload_file.subtask((pk, parenttmpdir, fil, ctype.id)) for fil in files])
        result = job.apply_async()
        data['success'] = '1'
    response['Content-Disposition'] = 'inline; filename=files.json'
    return JSONResponse([data], {}, response_mimetype(request))

@csrf_exempt
def upload_image(request):
    # Force django to save all files to disk as temporary
    request.upload_handlers.insert(0, TemporaryFileUploadHandler())

    # Json response
    data = {"jsonrpc" : "2.0", "id" : "id"}

    file_ = request.FILES.get('file')

    ctype, pk = get_ctype(request, UPLOADIT_PARENT_CLASS)

    if image and ctype and pk:
        try:
            # pk needs to be Primary Key value. Because of the generic fk field.
            parent = ctype.get_object_for_this_type(pk=pk)
        except ctype.model_class().DoesNotExist:
            data["error"] = {"code": 102, "message": 
                                "Failed to upload file. %s object with pk %s Doesn't exist." % (ctype.model_class().__class__.__name__, pk)}
        else:
            date = getattr(parent, UPLOADIT_PARENT_DATETIME)
            foldername = get_timestamp(date) + pk
            parentpath = os.path.join(UPLOADIT_TEMP_FILES, foldername)
            if not os.path.exists(parentpath):
                os.mkdir(parentpath)
            task_process_file.apply_async(args=[parentpath, file_.temporary_file_path(), file_.name], countdown=0)
            data["result"] = "null"
    else:
        data["error"] = {"code": 102, "message": "Failed to upload file."}
    response = JSONResponse([data], {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = simplejson.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)
