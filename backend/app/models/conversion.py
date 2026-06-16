import enum
from datetime import datetime
from sqlalchemy import String, Enum, DateTime, Text, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class ConversionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversionTask(Base):
    __tablename__ = "conversion_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_format: Mapped[str] = mapped_column(String(20), nullable=False)
    target_format: Mapped[str] = mapped_column(String(20), nullable=False)
    conversion_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[ConversionStatus] = mapped_column(
        Enum(ConversionStatus), default=ConversionStatus.PENDING
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)
    minio_input_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    minio_output_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    output_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    output_file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
