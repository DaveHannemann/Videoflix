from .models import Video
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import os
from .tasks import process_video
import django_rq
import shutil

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video wurde gespeichert')
    if created:
        print(f"New video uploaded: {instance.title}")
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(process_video, instance.id)



@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):

    files = [
        instance.video_file.path,
        instance.video_file.path.replace(".mp4", "_480p.mp4"),
        instance.video_file.path.replace(".mp4", "_720p.mp4"),
        instance.video_file.path.replace(".mp4", "_1080p.mp4"),
    ]

    if instance.thumbnail:
        files.append(instance.thumbnail.path)

    for file_path in files:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")

    hls_dir = os.path.splitext(instance.video_file.path)[0]

    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)