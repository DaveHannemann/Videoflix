import subprocess
import os
from django.conf import settings

from videos.models import Video

def generate_thumbnail(source):
    """
    Generates a thumbnail image from the uploaded video.

    Extracts a single frame five seconds into the video
    and stores it as a JPEG image.
    """
    
    filename = os.path.basename(source).replace(
        ".mp4",
        "_thumbnail.jpg"
    )

    thumbnail_path = os.path.join(
        os.path.dirname(os.path.dirname(source)),
        "thumbnails",
        filename
    )

    os.makedirs(
        os.path.dirname(thumbnail_path),
        exist_ok=True
    )

    subprocess.run(
        [
            "ffmpeg",
            "-ss", "5",
            "-i", source,
            "-vframes", "1",
            thumbnail_path,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return f"thumbnails/{filename}"


def create_hls(source, video_id, resolution):
    """
    Converts a video into an HLS stream.

    Generates an HLS playlist and MPEG-TS segments
    for the specified resolution.
    """

    output_dir = os.path.join(
        settings.MEDIA_ROOT,
        "hls",
        str(video_id),
        resolution,
    )

    os.makedirs(output_dir, exist_ok=True)

    resolutions = {
        "480p": "854:480",
        "720p": "1280:720",
        "1080p": "1920:1080",
    }
    if resolution not in resolutions:
        raise ValueError(f"Unknown resolution: {resolution}")

    subprocess.run(
        [
            "ffmpeg",
            "-i", source,
            "-vf", f"scale={resolutions[resolution]}",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-hls_time", "10",
            "-hls_playlist_type", "vod",
            "-hls_segment_filename",
            os.path.join(output_dir, "segment_%03d.ts"),
            os.path.join(output_dir, "index.m3u8"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def process_video(video_id):
    """
    Processes an uploaded video.

    Generates a thumbnail image and creates HLS streams
    in multiple resolutions for adaptive video streaming.
    """

    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return

    thumbnail = generate_thumbnail(
        video.video_file.path
    )

    video.thumbnail = thumbnail
    video.save(update_fields=["thumbnail"])

    create_hls(video.video_file.path, video.id, "480p")
    create_hls(video.video_file.path, video.id, "720p")
    create_hls(video.video_file.path, video.id, "1080p")