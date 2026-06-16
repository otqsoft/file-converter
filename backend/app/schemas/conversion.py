from datetime import datetime
from pydantic import BaseModel
from ..models.conversion import ConversionStatus


class ConversionTaskCreate(BaseModel):
    filename: str
    original_format: str
    target_format: str
    conversion_type: str


class ConversionTaskResponse(BaseModel):
    id: int
    filename: str
    original_format: str
    target_format: str
    conversion_type: str
    status: ConversionStatus
    progress: int
    output_filename: str | None
    file_size: int
    output_file_size: int | None
    duration: float | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversionTaskListResponse(BaseModel):
    total: int
    items: list[ConversionTaskResponse]
