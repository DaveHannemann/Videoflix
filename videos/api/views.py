import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videos.models import Video
from .serializers import VideoSerializer
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404


class VideoUploadView(APIView):
    """
    Handles video uploads.

    Allows administrators to upload new videos.
    Uploaded videos are stored and automatically processed
    in the background (thumbnail generation and HLS conversion).

    Permissions:
        - Admin users only
    """

    permission_classes = [IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VideoListView(ListAPIView):
    """
    Returns a list of all available videos.

    Provides video metadata including title, description,
    category, creation date and thumbnail URL.

    Permissions:
        - Authenticated users only
    """

    permission_classes = [IsAuthenticated]

    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class PlaylistView(APIView):
    """
    Serves the HLS playlist for a specific video and resolution.

    Returns the requested M3U8 playlist file used by
    HLS-compatible video players.

    URL Parameters:
        - movie_id: Video ID
        - resolution: Video quality (480p, 720p, 1080p)

    Permissions:
        - Authenticated users only
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):

        video = get_object_or_404(Video, pk=movie_id)

        playlist = os.path.join(
            settings.MEDIA_ROOT,
            "hls",
            str(movie_id),
            resolution,
            "index.m3u8",
        )

        if not os.path.exists(playlist):
            raise Http404("Playlist not found.")

        return FileResponse(
            open(playlist, "rb"),
            content_type="application/vnd.apple.mpegurl",
        )
    
class SegmentView(APIView):
    """
    Serves individual HLS video segments.

    Returns the requested MPEG-TS segment belonging to
    a specific video and resolution.

    URL Parameters:
        - movie_id: Video ID
        - resolution: Video quality (480p, 720p, 1080p)
        - segment: Segment filename

    Permissions:
        - Authenticated users only
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):

        video = get_object_or_404(Video, pk=movie_id)

        segment_path = os.path.join(
            settings.MEDIA_ROOT,
            "hls",
            str(movie_id),
            resolution,
            segment,
        )

        if not os.path.exists(segment_path):
            raise Http404("Segment not found.")

        return FileResponse(
            open(segment_path, "rb"),
            content_type="video/MP2T",
        )