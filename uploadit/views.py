import os
from datetime import datetime


from django.utils import simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.conf import settings

from uploadit.tasks import task_upload_file, task_process_file
from uploadit.utils import get_ctype, get_timestamp


UPLOADIT_TEMP_FILES = settings.UPLOADIT_TEMP_FILES
UPLOADIT_PARENT_CLASS = settings.UPLOADIT_PARENT_CLASS
UPLOADIT_PARENT_DATETIME = settings.UPLOADIT_PARENT_DATETIME


@csrf_exempt
def upload_image(request):
    # Force django to save all files to disk as temporary
    request.upload_handlers.insert(0, TemporaryFileUploadHandler())
    print "RUNNNING"
    # Json response
    data = {"jsonrpc" : "2.0", "id" : "id"}

    file_ = request.FILES.get('file')

    # This defines whether the upload is direct ( '1' ), meaning that its uploaded instantly in one task.
    # Or not direct ( '0' ) in which case it splits the upload in two tasks. Which requires dev to
    # explicitly call uploadit.utils.upload_images once all files have been proccessed,
    # which creates a task set of task_upload_file tasks for each file.

    direct = request.POST.get('direct', '0')

    ctype, pk = get_ctype(request, UPLOADIT_PARENT_CLASS)

    if file_ and ctype and pk:
        try:
            # pk needs to be Primary Key value. Because of the generic fk field.
            parent = ctype.get_object_for_this_type(pk=pk)
        except ctype.model_class().DoesNotExist:
            data["error"] = {"code": 102, "message": 
                                "Failed to upload file. %s object with pk %s Doesn't exist." % (ctype.model_class().__class__.__name__, pk)}
        else:
            if direct == '0':
                date = getattr(parent, UPLOADIT_PARENT_DATETIME)
                foldername = get_timestamp(date) + pk
                parentpath = os.path.join(UPLOADIT_TEMP_FILES, foldername)
                if not os.path.exists(parentpath):
                    os.mkdir(parentpath)
                    task_process_file.apply_async(args=[parentpath, file_.temporary_file_path(), file_.name], countdown=0)
                    #data["result"] = task.task_id
            else:
                task_upload_file.apply_async(args=[pk, file_.temporary_file_path(), ctype.id, file_.name], countdown=0)
                #data["result"] = task.task_id
    else:
        data["error"] = {"code": 102, "message": "Failed to upload file."}
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')
