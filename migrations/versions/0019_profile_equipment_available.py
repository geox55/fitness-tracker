"""user_profiles.equipment_available — spec 004 REQ-09.

Revision ID: 0019_profile_equipment
Revises: 0012_exercises_owner

`equipment_available` — список оборудования, доступного пользователю
(спортзал / домашний / только bodyweight и т.д.). Используется AI-генератором
тренировок (spec 006 Scenario 2): в план попадают только упражнения,
у которых `equipment ⊆ user.equipment_available`.

NULL означает «пользователь не настраивал» — генератор тогда берёт
DEFAULT_EQUIPMENT_AVAILABLE (типовой коммерческий зал). Пустой `[]`
означает явно настроенный «ничего из оборудования» — этот случай тоже
валиден и генератор отдаст только bodyweight-упражнения.

Контракт на значения (enum spec 004 §6) валидируется в pydantic-схеме
ProfileUpdateRequest; в БД храним как TEXT[] без CHECK — иначе при
расширении enum'а пришлось бы делать миграцию ради нового значения.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "0019_profile_equipment"
down_revision: str | None = "0012_exercises_owner"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column(
            "equipment_available",
            ARRAY(sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "equipment_available")
