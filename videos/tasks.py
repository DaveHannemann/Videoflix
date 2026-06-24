import subprocess
import os

from videos.models import Video

def convert_480p(source):
    new_file_name = source.replace(".mp4", "_480p.mp4")

    subprocess.run(
        [
            "ffmpeg",
            "-i", source,
            "-s", "hd480",
            "-c:v", "libx264",
            "-crf", "23",
            "-c:a", "aac",
            new_file_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return new_file_name

def convert_720p(source):
    new_file_name = source.replace(".mp4", "_720p.mp4")

    subprocess.run(
        [
            "ffmpeg",
            "-i", source,
            "-s", "hd720",
            "-c:v", "libx264",
            "-crf", "23",
            "-c:a", "aac",
            new_file_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return new_file_name

def convert_1080p(source):
    new_file_name = source.replace(".mp4", "_1080p.mp4")

    subprocess.run(
        [
            "ffmpeg",
            "-i", source,
            "-s", "hd1080",
            "-c:v", "libx264",
            "-crf", "23",
            "-c:a", "aac",
            new_file_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return new_file_name

def generate_thumbnail(source):
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

def process_video(video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return

    thumbnail = generate_thumbnail(
        video.video_file.path
    )

    video.thumbnail = thumbnail
    video.save(update_fields=["thumbnail"])

    convert_480p(video.video_file.path)
    convert_720p(video.video_file.path)
    convert_1080p(video.video_file.path)
    create_hls(video.video_file.path, "480p")
    create_hls(video.video_file.path, "720p")
    create_hls(video.video_file.path, "1080p")


def create_hls(source, resolution):
    output_dir = source.replace(
        ".mp4",
        f"/{resolution}"
    )

    os.makedirs(output_dir, exist_ok=True)

    resolutions = {
        "480p": "854:480",
        "720p": "1280:720",
        "1080p": "1920:1080",
    }

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
            os.path.join(output_dir, "%03d.ts"),
            os.path.join(output_dir, "index.m3u8"),
        ],
        check=True,
    )