from django.conf import settings
from .models import Video
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import os
from .tasks import process_video
import django_rq
import shutil

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Enqueues background processing for newly uploaded videos.

    After a video has been created, a background job is added
    to the RQ queue to generate the thumbnail and HLS streams.
    """

    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(process_video, instance.id)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Removes all generated files associated with a deleted video.

    Deletes:
        - Original uploaded video
        - Generated thumbnail
        - HLS playlists and segments
    """

    files = [
        instance.video_file.path,
    ]

    if instance.thumbnail:
        files.append(instance.thumbnail.path)

    for file_path in files:
        if os.path.isfile(file_path):
            os.remove(file_path)

    hls_dir = os.path.join(
        settings.MEDIA_ROOT,
        "hls",
        str(instance.id),
    )

    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)