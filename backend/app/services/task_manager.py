import os
import shutil
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..config import settings
from ..models.conversion import ConversionTask, ConversionStatus
from ..schemas.conversion import ConversionTaskCreate
from .minio_service import MinioService
from .converter import ConverterService

OFFICE_FORMATS = {"doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "odp"}
MEDIA_FORMATS = {"avi", "mkv", "mov", "flv", "mp4", "gif", "webm", "mp3", "wav", "aac", "flac", "ogg"}
PDF_FORMAT = {"pdf"}
IMAGE_FORMATS = {"png", "jpg", "jpeg", "bmp", "gif", "tiff", "webp"}


class TaskManager:
    def __init__(self):
        self.minio = MinioService()
        self.converter = ConverterService()

    def detect_conversion_type(self, original_format: str, target_format: str) -> str:
        if original_format in OFFICE_FORMATS and target_format == "pdf":
            return "office_to_pdf"
        if original_format == "pdf" and target_format in ("docx", "doc"):
            return "pdf_to_word"
        if original_format == "pdf" and target_format in ("xlsx", "xls"):
            return "pdf_to_excel"
        if original_format == "pdf" and target_format in ("png", "jpg", "jpeg"):
            return "pdf_to_image"
        if original_format == "pdf" and target_format == "md":
            return "pdf_to_markdown"
        if original_format == "md" and target_format == "pdf":
            return "markdown_to_pdf"
        if original_format in IMAGE_FORMATS and target_format in IMAGE_FORMATS:
            return "image_to_image"
        if original_format in IMAGE_FORMATS and target_format == "pdf":
            return "image_to_pdf"
        if original_format in ("docx", "doc") and target_format in ("docx", "doc", "txt", "pdf"):
            return "word_convert"
        if original_format in ("xlsx", "xls") and target_format in ("xlsx", "xls", "csv", "pdf"):
            return "excel_convert"
        if original_format in MEDIA_FORMATS and target_format in MEDIA_FORMATS:
            return "media_convert"
        raise ValueError(f"Unsupported conversion: {original_format} -> {target_format}")

    async def create_task(self, db: AsyncSession, task_data: ConversionTaskCreate) -> ConversionTask:
        task = ConversionTask(
            filename=task_data.filename,
            original_format=task_data.original_format,
            target_format=task_data.target_format,
            conversion_type=task_data.conversion_type,
            status=ConversionStatus.PENDING,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def upload_and_start(self, db: AsyncSession, task_id: int, file_data: bytes, filename: str):
        task = await db.get(ConversionTask, task_id)
        if not task:
            return

        try:
            ext = Path(filename).suffix.lstrip(".")
            minio_key = f"uploads/{task_id}/{filename}"
            file_size = len(file_data)

            content_type = self._get_content_type(ext)
            self.minio.upload_file(minio_key, file_data, content_type)

            await db.execute(
                update(ConversionTask)
                .where(ConversionTask.id == task_id)
                .values(
                    status=ConversionStatus.PROCESSING,
                    minio_input_key=minio_key,
                    file_size=file_size,
                    progress=10,
                )
            )
            await db.commit()

            output_path = await self._do_convert(
                task_id, task.conversion_type, ext, task.target_format, filename
            )

            output_name = Path(output_path).name
            output_minio_key = f"outputs/{task_id}/{output_name}"
            with open(output_path, "rb") as f:
                output_data = f.read()
            self.minio.upload_file(
                output_minio_key, output_data, self._get_content_type(task.target_format)
            )

            os.remove(output_path)
            tmp_upload = settings.UPLOAD_DIR / str(task_id)
            if tmp_upload.exists():
                shutil.rmtree(tmp_upload)

            output_size = len(output_data)
            await db.execute(
                update(ConversionTask)
                .where(ConversionTask.id == task_id)
                .values(
                    status=ConversionStatus.COMPLETED,
                    minio_output_key=output_minio_key,
                    output_filename=output_name,
                    output_file_size=output_size,
                    progress=100,
                )
            )
            await db.commit()

        except Exception as e:
            await db.execute(
                update(ConversionTask)
                .where(ConversionTask.id == task_id)
                .values(
                    status=ConversionStatus.FAILED,
                    error_message=str(e)[:1000],
                )
            )
            await db.commit()

    async def _do_convert(
        self, task_id: int, conversion_type: str, original_format: str,
        target_format: str, filename: str
    ) -> str:
        upload_dir = settings.UPLOAD_DIR / str(task_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        input_path = str(upload_dir / filename)

        minio_data = self.minio.download_file(f"uploads/{task_id}/{filename}")
        with open(input_path, "wb") as f:
            f.write(minio_data.read())

        output_dir = settings.OUTPUT_DIR / str(task_id)
        output_dir.mkdir(parents=True, exist_ok=True)

        converters = {
            "office_to_pdf": lambda: self.converter.convert_office_to_pdf(input_path, str(output_dir)),
            "pdf_to_word": lambda: self.converter.convert_pdf_to_word(input_path, str(output_dir)),
            "pdf_to_excel": lambda: self.converter.convert_pdf_to_excel(input_path, str(output_dir)),
            "pdf_to_image": lambda: self.converter.convert_pdf_to_image(input_path, str(output_dir), target_format),
            "pdf_to_markdown": lambda: self.converter.convert_pdf_to_markdown(input_path, str(output_dir)),
            "markdown_to_pdf": lambda: self.converter.convert_markdown_to_pdf(input_path, str(output_dir)),
            "image_to_image": lambda: self.converter.convert_image_to_image(input_path, str(output_dir), target_format),
            "image_to_pdf": lambda: self.converter.convert_image_to_pdf(input_path, str(output_dir)),
            "word_convert": lambda: self.converter.convert_word_to_word(input_path, str(output_dir), target_format),
            "excel_convert": lambda: self.converter.convert_excel_to_excel(input_path, str(output_dir), target_format),
            "media_convert": lambda: self.converter.convert_media(input_path, str(output_dir), target_format),
        }

        converter_fn = converters.get(conversion_type)
        if not converter_fn:
            raise ValueError(f"Unknown conversion type: {conversion_type}")

        return converter_fn()

    def _get_content_type(self, ext: str) -> str:
        types = {
            "pdf": "application/pdf",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xls": "application/vnd.ms-excel",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "ppt": "application/vnd.ms-powerpoint",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "mp4": "video/mp4",
            "avi": "video/x-msvideo",
            "mkv": "video/x-matroska",
            "mov": "video/quicktime",
            "flv": "video/x-flv",
            "webm": "video/webm",
            "gif": "image/gif",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "aac": "audio/aac",
            "flac": "audio/flac",
            "ogg": "audio/ogg",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "bmp": "image/bmp",
            "tiff": "image/tiff",
            "webp": "image/webp",
            "md": "text/markdown",
            "txt": "text/plain",
            "csv": "text/csv",
            "zip": "application/zip",
        }
        return types.get(ext, "application/octet-stream")

    def get_download_url(self, task: ConversionTask) -> str | None:
        if task.minio_output_key:
            return self.minio.get_presigned_url(task.minio_output_key, expires=3600)
        return None
