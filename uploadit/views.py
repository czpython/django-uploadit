import os
import ipdb


from django.utils import simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from uploadit.tasks import task_upload_file
from uploadit.uploadhandler import UploaditFileUploadHandler


@csrf_exempt
def upload_image(request):
    # Force django to save all files to disk as temporary
    request.upload_handlers.insert(0, UploaditFileUploadHandler())
    # Json response
    data = {"jsonrpc" : "2.0", "id" : "id"}

    files = request.FILES

    # Unique ID used to group a set of files together.
    groupid = request.POST.get('groupid')

    try:
        count = int(request.POST.get('count'))
    except TypeError, e:
        count = None

    if files:
        # All files are uploaded to disk.
        for name, file_ in files.iteritems():
            path = file_.file_path()
            task = task_upload_file.delay(path, file_.name, filecount=count, group=groupid)
            data['%s_task_id' % name] = task.id
    else:
        data["error"] = {"code": 102, "message": "No File was received."}
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')
