from django.urls import path
from .views import VideoUploadView

urlpatterns = [
    path('videos/', VideoUploadView.as_view(), name='video-upload'),
]