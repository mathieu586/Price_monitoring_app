import logging
import os
import sys
from pathlib import Path

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def get_converted_directory(default = "converted"):
    env_val = os.environ.get("CONVERTED_DIR", "").strip()
    directory = Path(env_val) if env_val else Path.cwd() / default
    directory.mkdir(parents=True, exist_ok=True)
    return directory

VIDEO_AUDIO_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
    ".webm", ".m4v", ".mpeg", ".mpg", ".ts",
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",}

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
    ".tif", ".webp", ".svg", ".heic", ".heif",
}

def is_video_audio(path):
    return path.suffix.lower() in VIDEO_AUDIO_EXTENSIONS

def is_image(path):
    return path.suffix.lower() in IMAGE_EXTENSIONS

def is_media_file(path):
    return is_video_audio(path) or is_image(path)

def find_media(directory):
    return [p for p in sorted(directory.rglob("*")) if p.is_file() and is_media_file(p)]