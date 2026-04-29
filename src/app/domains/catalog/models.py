import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exercise_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    exercise_name: Mapped[str] = mapped_column(Text, nullable=False)
    exercise_name_ru: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_muscle_group: Mapped[str] = mapped_column(String, nullable=False)
    secondary_muscle_group: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    equipment: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    calories_burned_per_hour: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    body_region: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
