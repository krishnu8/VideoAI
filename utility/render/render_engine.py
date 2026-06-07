import time
import os
import tempfile
import platform
import subprocess
from typing import Callable, Optional

# Monkey-patch PIL.Image.ANTIALIAS for MoviePy compatibility with Pillow >= 10.0.0
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'Resampling', PIL.Image).LANCZOS

from moviepy.editor import (
    AudioFileClip, CompositeVideoClip, CompositeAudioClip,
    ImageClip, VideoFileClip, TextClip
)
import requests
from utility.config import get_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def download_file(url: str, filename: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    with open(filename, "wb") as f:
        response = requests.get(url, headers=headers, timeout=60)
        f.write(response.content)


def search_program(program_name: str) -> Optional[str]:
    try:
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None


def get_program_path(program_name: str) -> Optional[str]:
    return search_program(program_name)


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def get_output_media(
    audio_file_path: str,
    timed_captions: list,
    background_video_data: list,
    video_server: str,
    output_path: Optional[str] = None,
    mode: str = "video",          # "video" | "image" | "mix"
    progress_callback: Optional[Callable[[str, int], None]] = None,
    orientation_landscape: bool = False,
    captions_enabled: bool = True,
) -> str:
    """
    Render the final video by compositing background media (video clips or
    images) with the narration audio.

    Parameters
    ----------
    audio_file_path     : path to narration audio (.mp3 / .wav)
    timed_captions      : list of ((t1, t2), text) from Whisper
    background_video_data : list of ([t1, t2], url) — can be video OR image URLs
    video_server        : "pexel" (kept for compatibility)
    output_path         : destination .mp4 path; auto-generated if None
    mode                : "video", "image", or "mix"
    progress_callback   : optional fn(message, percent_0_to_100)
    orientation_landscape : True = 1920×1080, False = 1080×1920
    """

    def _cb(msg: str, pct: int):
        if progress_callback:
            progress_callback(msg, pct)

    config = get_config()

    # --- Output file ---
    if output_path is None:
        output_path = "rendered_video.mp4"

    # --- ImageMagick ---
    magick_path = get_program_path("magick")
    if magick_path:
        os.environ["IMAGEMAGICK_BINARY"] = magick_path
    else:
        os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

    # --- Resolution ---
    if orientation_landscape:
        VIDEO_WIDTH, VIDEO_HEIGHT = 1920, 1080
    else:
        VIDEO_WIDTH, VIDEO_HEIGHT = 1080, 1920

    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    temp_files: list[str] = []
    visual_clips = []

    _cb("Downloading and processing media segments...", 5)

    # Detect whether each URL is a video or image by its extension / mode
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    def _is_image_url(url: str) -> bool:
        if not url:
            return False
        lower = url.lower().split("?")[0]  # strip query string
        return any(lower.endswith(ext) for ext in IMAGE_EXTS) or "pexels.com/photo" in lower

    # Build background clip list
    concat_file_path = None

    if mode in ("video", "mix") and any(
        not _is_image_url(u) for _, u in background_video_data if u
    ):
        # --- FFmpeg concat for video segments ---
        concat_tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".txt", mode="w", encoding="utf-8"
        )
        temp_files.append(concat_tmp.name)
        concat_file_path = concat_tmp.name

        for idx, ((t1, t2), media_url) in enumerate(background_video_data):
            if not media_url:
                continue
            duration = t2 - t1

            if _is_image_url(media_url) or mode == "image":
                # Render image as a still clip via FFmpeg
                img_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                raw_img_path = img_tmp.name
                img_tmp.close()
                temp_files.append(raw_img_path)

                try:
                    download_file(media_url, raw_img_path)
                except Exception as e:
                    print(f"Image download failed ({media_url[:60]}): {e}")
                    continue

                part_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                part_path = part_tmp.name
                part_tmp.close()
                temp_files.append(part_path)

                cmd = [
                    ffmpeg_path, "-y",
                    "-loop", "1",
                    "-i", raw_img_path,
                    "-t", str(duration),
                    "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
                           f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "28",
                    "-an",
                    part_path,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                safe_path = part_path.replace("\\", "/")
                concat_tmp.write(f"file '{safe_path}'\n") if not concat_tmp.closed else None

            else:
                # Standard video download + trim
                raw_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                raw_path = raw_tmp.name
                raw_tmp.close()
                temp_files.append(raw_path)

                try:
                    download_file(media_url, raw_path)
                except Exception as e:
                    print(f"Video download failed ({media_url[:60]}): {e}")
                    continue

                part_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                part_path = part_tmp.name
                part_tmp.close()
                temp_files.append(part_path)

                cmd = [
                    ffmpeg_path, "-y",
                    "-i", raw_path,
                    "-t", str(duration),
                    "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "28",
                    "-an",
                    part_path,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                safe_path = part_path.replace("\\", "/")
                # Re-open for writing if needed
                with open(concat_file_path, "a", encoding="utf-8") as cf:
                    cf.write(f"file '{safe_path}'\n")

            pct = int((idx + 1) / len(background_video_data) * 60)
            _cb(f"Processed segment {idx+1}/{len(background_video_data)}", pct)

        concat_tmp.close()

    else:
        # Pure image mode — build concat file fresh
        concat_tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".txt", mode="w", encoding="utf-8"
        )
        concat_file_path = concat_tmp.name
        temp_files.append(concat_file_path)

        for idx, ((t1, t2), media_url) in enumerate(background_video_data):
            if not media_url:
                continue
            duration = t2 - t1

            img_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            raw_img_path = img_tmp.name
            img_tmp.close()
            temp_files.append(raw_img_path)

            try:
                download_file(media_url, raw_img_path)
            except Exception as e:
                print(f"Image download failed: {e}")
                continue

            part_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            part_path = part_tmp.name
            part_tmp.close()
            temp_files.append(part_path)

            cmd = [
                ffmpeg_path, "-y",
                "-loop", "1",
                "-i", raw_img_path,
                "-t", str(duration),
                "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
                       f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "28",
                "-an",
                part_path,
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            safe_path = part_path.replace("\\", "/")
            concat_tmp.write(f"file '{safe_path}'\n")
            pct = int((idx + 1) / len(background_video_data) * 60)
            _cb(f"Processed image {idx+1}/{len(background_video_data)}", pct)

        concat_tmp.close()

    # --- Concatenate all parts ---
    _cb("Concatenating media segments...", 65)
    bg_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    bg_filename = bg_tmp.name
    bg_tmp.close()
    temp_files.append(bg_filename)

    cmd_concat = [
        ffmpeg_path, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file_path,
        "-c", "copy",
        bg_filename,
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # --- Composite with MoviePy ---
    _cb("Compositing video and audio...", 75)
    background_clip = VideoFileClip(bg_filename)
    visual_clips.append(background_clip)

    # --- Add Captions ---
    if captions_enabled:
        _cb("Rendering captions...", 80)
        font_size = config.get_caption_font_size()
        font_color = config.get_caption_font_color()
        stroke_width = config.get_caption_stroke_width()
        stroke_color = config.get_caption_stroke_color()
        font_face = config.get_caption_font_face()
        caption_position = config.get_caption_position()

        bottom_y = VIDEO_HEIGHT - 150
        mid_y = VIDEO_HEIGHT // 2

        if caption_position == 'bottom_center':
            position = ("center", bottom_y)
        elif caption_position == 'bottom_left':
            position = ("left", bottom_y)
        elif caption_position == 'bottom_right':
            position = ("right", bottom_y)
        elif caption_position == 'top':
            position = ("center", 100)
        elif caption_position == 'center':
            position = ("center", mid_y)
        else:
            position = ("center", bottom_y)

        for (t1, t2), text in timed_captions:
            try:
                # TextClip requires ImageMagick to be configured correctly
                text_clip = TextClip(
                    txt=text,
                    font=font_face,
                    fontsize=font_size,
                    color=font_color,
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    method="label"
                )
                text_clip = text_clip.set_start(t1).set_end(t2).set_position(position)
                visual_clips.append(text_clip)
            except Exception as e:
                print(f"Failed to generate caption for text '{text}': {e}")

    audio_file_clip = AudioFileClip(audio_file_path)

    video = CompositeVideoClip(visual_clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    audio = CompositeAudioClip([audio_file_clip])
    video.duration = audio.duration
    video.audio = audio

    _cb("Writing final video file...", 85)
    video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=25,
        preset="veryfast",
        threads=2,
        logger=None,
    )

    # --- Cleanup ---
    _cb("Cleaning up temp files...", 98)
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception:
            pass

    return output_path
