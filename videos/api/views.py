from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videos.models import Video
from .serializers import VideoSerializer
from rest_framework.generics import ListAPIView


class VideoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer