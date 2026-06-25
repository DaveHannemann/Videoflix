from django.db import models

# Create your models here.
class Video(models.Model):
    """
    Represents a video available for streaming.

    Stores the video's metadata, original uploaded file,
    and the generated thumbnail image.
    """
    
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    category = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')
    
    def __str__(self):
        return self.title