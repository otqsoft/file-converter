import os
import subprocess
import shutil
from pathlib import Path
from ..config import settings


class ConverterService:
    @staticmethod
    def convert_office_to_pdf(input_path: str, output_dir: str) -> str:
        cmd = [
            settings.LIBREOFFICE_PATH,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")

        input_name = Path(input_path).stem
        output_path = os.path.join(output_dir, f"{input_name}.pdf")
        if not os.path.exists(output_path):
            raise RuntimeError(f"Output file not found: {output_path}")
        return output_path

    @staticmethod
    def convert_media(input_path: str, output_dir: str, target_format: str) -> str:
        input_name = Path(input_path).stem
        output_path = os.path.join(output_dir, f"{input_name}.{target_format}")

        cmd = [
            settings.FFMPEG_PATH,
            "-y",
            "-i", input_path,
        ]

        if target_format == "gif":
            cmd.extend([
                "-vf", "fps=10,scale=480:-1:flags=lanczos",
                "-loop", "0",
            ])
        elif target_format in ("mp3", "wav", "aac", "flac", "ogg"):
            cmd.extend(["-vn", "-acodec", "libmp3lame", "-q:a", "2"])
        elif target_format in ("mp4", "mkv", "avi", "mov", "flv", "webm"):
            cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-strict", "experimental"])

        cmd.append(output_path)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")

        if not os.path.exists(output_path):
            raise RuntimeError(f"Output file not found: {output_path}")
        return output_path

    @staticmethod
    def get_media_info(file_path: str) -> dict:
        cmd = [
            settings.FFMPEG_PATH,
            "-i", file_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        info_str = result.stderr

        duration = 0.0
        for line in info_str.split("\n"):
            if "Duration:" in line:
                dur_str = line.split("Duration:")[1].split(",")[0].strip()
                parts = dur_str.split(":")
                if len(parts) == 3:
                    duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break

        return {"duration": duration, "raw": info_str}
