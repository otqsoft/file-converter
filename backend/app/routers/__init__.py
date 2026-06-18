from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from urllib.parse import quote
from ..database import get_db
from ..models.conversion import ConversionTask, ConversionStatus
from ..schemas.conversion import ConversionTaskResponse, ConversionTaskListResponse
from ..services.task_manager import TaskManager

router = APIRouter(prefix="/api/conversions", tags=["conversions"])

task_manager = TaskManager()

OFFICE_FORMATS = {"doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "odp"}
MEDIA_FORMATS = {"avi", "mkv", "mov", "flv", "mp4", "gif", "webm", "mp3", "wav", "aac", "flac", "ogg"}
PDF_FORMATS = {"pdf"}
IMAGE_FORMATS = {"png", "jpg", "jpeg", "bmp", "gif", "tiff", "webp"}


@router.post("/upload", response_model=ConversionTaskResponse)
async def upload_and_convert(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_format: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    try:
        conversion_type = task_manager.detect_conversion_type(ext, target_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task_data = {
        "filename": file.filename,
        "original_format": ext,
        "target_format": target_format,
        "conversion_type": conversion_type,
    }
    from ..schemas.conversion import ConversionTaskCreate
    task = await task_manager.create_task(db, ConversionTaskCreate(**task_data))

    file_data = await file.read()

    background_tasks.add_task(task_manager.upload_and_start, db, task.id, file_data, file.filename)

    return task


@router.get("/", response_model=ConversionTaskListResponse)
async def list_tasks(
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = select(ConversionTask)
    count_query = select(func.count(ConversionTask.id))

    if status:
        try:
            status_enum = ConversionStatus(status)
            query = query.where(ConversionTask.status == status_enum)
            count_query = count_query.where(ConversionTask.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(desc(ConversionTask.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return ConversionTaskListResponse(total=total, items=items)


@router.get("/active", response_model=ConversionTaskListResponse)
async def list_active_tasks(db: AsyncSession = Depends(get_db)):
    query = (
        select(ConversionTask)
        .where(ConversionTask.status.in_([ConversionStatus.PENDING, ConversionStatus.PROCESSING]))
        .order_by(desc(ConversionTask.created_at))
    )
    result = await db.execute(query)
    items = result.scalars().all()
    return ConversionTaskListResponse(total=len(items), items=items)


@router.get("/{task_id}/download")
async def download_result(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(ConversionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != ConversionStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Task not completed")
    if not task.minio_output_key:
        raise HTTPException(status_code=404, detail="Output file not found")

    file_data = task_manager.minio.download_file(task.minio_output_key)
    file_bytes = file_data.read()

    content_type_map = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "mp4": "video/mp4",
        "avi": "video/x-msvideo",
        "mkv": "video/x-matroska",
        "mov": "video/quicktime",
        "flv": "video/x-flv",
        "webm": "video/webm",
        "gif": "image/gif",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "bmp": "image/bmp",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "ogg": "audio/ogg",
        "md": "text/markdown",
        "txt": "text/plain",
        "csv": "text/csv",
        "zip": "application/zip",
    }
    content_type = content_type_map.get(task.target_format, "application/octet-stream")
    filename = task.output_filename or f"output.{task.target_format}"

    # RFC 5987 编码：处理非 ASCII 文件名（如中文），避免 HTTP 头部编码错误
    quoted_filename = quote(filename)
    content_disposition = f"attachment; filename=\"{quoted_filename}\"; filename*=UTF-8''{quoted_filename}"

    from fastapi.responses import Response
    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": content_disposition},
    )


@router.get("/{task_id}", response_model=ConversionTaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(ConversionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(ConversionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.minio_input_key:
        try:
            task_manager.minio.delete_file(task.minio_input_key)
        except Exception:
            pass
    if task.minio_output_key:
        try:
            task_manager.minio.delete_file(task.minio_output_key)
        except Exception:
            pass

    await db.delete(task)
    await db.commit()
    return {"detail": "Task deleted"}
