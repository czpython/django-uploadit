from django.conf.urls.defaults import *


urlpatterns = patterns('uploadit.views',
    url(r'^uploadit/upload/$', 'upload_images', name="uploadit-upload-images"),
    url(r'^uploadit/image/upload/$', 'upload_image', name="uploadit-upload-image"),
)