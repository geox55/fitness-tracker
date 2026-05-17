import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
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
    # NULL → глобальный каталог (сидинг), виден всем.
    # NOT NULL → пользовательское: видно только владельцу, редактируется/удаляется
    # им же. Spec 014. На уровне таблицы owner_id nullable; FK CASCADE удаляет
    # упражнение при удалении пользователя.
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class UserExerciseFavorite(Base):
    """Связь user→exercise со звёздочкой. Spec 014.

    Композитный PK (user_id, exercise_id) обеспечивает идемпотентность POST
    /exercises/{id}/favorite: повторный INSERT падает в UniqueViolation, который
    сервис ловит как «уже добавлено» и возвращает 204.
    """

    __tablename__ = "user_exercise_favorites"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
