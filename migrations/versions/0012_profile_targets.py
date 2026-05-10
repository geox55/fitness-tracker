"""user_profiles: target_weight_kg, target_muscle_kg, goal_started_at.

Опциональные поля для прогресс-бара цели (REQ-06 spec 010): пользователь
указывает их в профиле — без них раздел «Прогресс по цели» показывает CTA.
`goal_started_at` — дата старта; нужна, чтобы стартовое значение для
прогресса бралось не «весь baseline», а с момента, когда пользователь начал
работать над целью (важно при смене цели в середине процесса).

Все три nullable: для существующих пользователей значения отсутствуют, в
UI они увидят CTA, как и для пользователей без цели вовсе.

Revision ID: 0012_profile_targets
Revises: 0011_pdf_key
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012_profile_targets"
down_revision: str | None = "0011_pdf_key"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("target_weight_kg", sa.Numeric(5, 2), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("target_muscle_kg", sa.Numeric(5, 2), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("goal_started_at", sa.Date(), nullable=True),
    )
    # Диапазоны совпадают с теми, что валидирует API (см. ProfileUpdateRequest).
    # Дублируем здесь, чтобы прямые INSERT'ы (миграции данных, скрипты)
    # тоже отлавливались — это типичное правило для check-constraints.
    op.create_check_constraint(
        "ck_user_profiles_target_weight_kg",
        "user_profiles",
        "target_weight_kg IS NULL OR target_weight_kg BETWEEN 30 AND 300",
    )
    op.create_check_constraint(
        "ck_user_profiles_target_muscle_kg",
        "user_profiles",
        "target_muscle_kg IS NULL OR target_muscle_kg BETWEEN 5 AND 120",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_user_profiles_target_muscle_kg", "user_profiles", type_="check"
    )
    op.drop_constraint(
        "ck_user_profiles_target_weight_kg", "user_profiles", type_="check"
    )
    op.drop_column("user_profiles", "goal_started_at")
    op.drop_column("user_profiles", "target_muscle_kg")
    op.drop_column("user_profiles", "target_weight_kg")
