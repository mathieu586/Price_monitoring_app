import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from utils import (
    get_converted_directory,
    get_logger,
    find_media,
    is_video_audio,
    is_image,
)

logger = get_logger("mediaconvert")

def get_output_name(original, format):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{original}.{format}"

def convert_ffmpeg(input_path, output_path):
    command = [
        "ffmpeg", "-y", "-i", str(input_path),str(output_path),
    ]
    logger.info(f"Converting ffmpeg: {input_path} to {output_path}")
    res = subprocess.run(command, capture_output=True, text=True)
    if res.returncode != 0:
        logger.error(f"ffmpeg error:\n{res.stderr}")
        return False, res.stderr
    return True, ""

def convert_imagemagick(input_path, output_path):
    for command_name in ("magick", "convert"):
        command = [command_name, str(input_path), str(output_path)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"{command_name}: {input_path.name} to {output_path.name}")
            return True, command_name
        if "not found" not in result.stderr.lower() and result.returncode != 127:
            logger.error(f"{command_name} error:\n{result.stderr}")
            return False, ""
    logger.error(f"ImageMagick nie jest zainstalowany")
    return False, ""

def convert_file(input_path, output_directory, output_format):
    output_name = get_output_name(input_path.stem, output_format)
    output_path = output_directory / output_name
    timestamp = datetime.now().isoformat()
    tool = ""
    if is_video_audio(input_path):
        succes, _ = convert_ffmpeg(input_path, output_path)
        tool = "ffmpeg"
    elif is_image(input_path):
        succes, tool = convert_imagemagick(input_path, output_path)
        if not tool:
            tool = "imagemagick"
    else:
        logger.warning(f"Nieznany typ pliku {input_path.name}")
        return None
    if not succes:
        return None

    return {
        "timestamp": timestamp,
        "input_path": str(input_path),
        "output_format": output_format,
        "output_path": str(output_path),
        "tool": tool,
    }

def load_history(history_path):
    if history_path.exists():
        try:
            return json.loads(history_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning(f"Błąd pliku {history_path}")
    return []

def save_history(history_path, history):
    history_path.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    logger.info(f"Historia zapisana: {history_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--format",required=True,dest="output_format")
    args = parser.parse_args()
    source_directory = Path(args.directory)
    if not source_directory.is_dir():
        logger.error(f"{source_directory} nie jest katalogiem")
        sys.exit(1)
    output_directory = get_converted_directory()
    history_path = output_directory / "history.json"
    logger.info(f"Katalog źródłowy : {source_directory}")
    logger.info(f"Katalog docelowy : {output_directory}")
    logger.info(f"Format wyjściowy : {args.output_format}")

    files = find_media(source_directory)
    if not files:
        logger.warning("Nie znaleziono plików")
        return
    logger.info(f"Znaleziono {len(files)} plików")
    history = load_history(history_path)

    for f in files:
        logger.info(f"Przetwarzam {f.name}")
        entry = convert_file(f, output_directory, args.output_format)
        if entry:
            history.append(entry)
            logger.info(f"Gotowe: {f.name}")
        else:
            logger.info(f"Błąd konwersji: {f.name}")
    save_history(history_path, history)
    logger.info("Zakończono konwersje")

if __name__ == "__main__":
    main()