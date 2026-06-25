from rest_framework import serializers
from videos.models import Video

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializes video metadata for the video list endpoint.

    Includes a dynamically generated absolute URL for the
    video's thumbnail image.
    """

    thumbnail_url = serializers.SerializerMethodField()

    
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']

    def get_thumbnail_url(self, obj):
        """
        Returns the absolute URL of the video's thumbnail.

        If no thumbnail or request object is available,
        None is returned.
        """

        request = self.context.get("request")

        if obj.thumbnail and request:
            return request.build_absolute_uri(
                obj.thumbnail.url
            )

        return None