"""Integration: spec 016 — суперсеты в логе тренировки.

Покрытие:
- POST /workouts/{id}/supersets/group: атомарно ставит общий group_id;
- POST /workouts/{id}/supersets/ungroup: сбрасывает в NULL;
- REQ-05: новый POST /logs наследует superset_group_id от существующего
  лога этого же упражнения в группе.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.catalog.models import Exercise
from app.domains.profile.models import UserProfile
from app.domains.workouts.models import ExerciseLog
from app.security import create_token


async def _seed_user_with_two_exercises(
    session: AsyncSession, *, email: str
) -> tuple[User, dict[str, str], uuid.UUID, uuid.UUID]:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    session.add(
        UserProfile(
            user_id=user.id,
            sex="male",
            height_cm=Decimal("180"),
            baseline_weight_kg=Decimal("80"),
            goal="muscle_gain",
            training_level="intermediate",
            training_frequency=3,
        )
    )
    # Два упражнения — суперсет «жим лёжа + тяга в наклоне».
    existing = (
        await session.execute(
            select(Exercise).where(
                Exercise.exercise_id.in_(["ss_bench", "ss_row"])
            )
        )
    ).scalars().all()
    by_slug = {e.exercise_id: e for e in existing}
    if "ss_bench" not in by_slug:
        ex_a = Exercise(
            exercise_id="ss_bench",
            exercise_name="Bench Press",
            primary_muscle_group="chest",
            secondary_muscle_group=[],
            instructions="",
            equipment=["barbell"],
            body_region="upper",
        )
        session.add(ex_a)
        by_slug["ss_bench"] = ex_a
    if "ss_row" not in by_slug:
        ex_b = Exercise(
            exercise_id="ss_row",
            exercise_name="Bent-Over Row",
            primary_muscle_group="back",
            secondary_muscle_group=[],
            instructions="",
            equipment=["barbell"],
            body_region="upper",
        )
        session.add(ex_b)
        by_slug["ss_row"] = ex_b
    await session.commit()

    token, _ = create_token(user_id=user.id, kind="access")
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers, by_slug["ss_bench"].id, by_slug["ss_row"].id


class TestSupersetGroupUngroup:
    async def test_group_assigns_same_id_to_all_logs(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        _, headers, ex_a, ex_b = await _seed_user_with_two_exercises(
            db_session, email="ss-1@example.com"
        )
        # Стартуем тренировку.
        w = (await client.post(
            "/api/v1/workouts", json={"origin": "freestyle"}, headers=headers
        )).json()
        wid = w["id"]
        # 2 подхода каждого упражнения.
        for ex_id in (ex_a, ex_b):
            for set_no in (1, 2):
                r = await client.post(
                    f"/api/v1/workouts/{wid}/logs",
                    json={
                        "exercise_id": str(ex_id),
                        "set_number": set_no,
                        "reps": 8,
                        "weight_kg": 60,
                    },
                    headers=headers,
                )
                assert r.status_code == 201, r.text

        # Все логи пока — group_id=NULL.
        all_logs = (
            await db_session.execute(
                select(ExerciseLog).where(ExerciseLog.workout_id == uuid.UUID(wid))
            )
        ).scalars().all()
        assert len(all_logs) == 4
        assert all(log.superset_group_id is None for log in all_logs)

        # Группируем.
        r = await client.post(
            f"/api/v1/workouts/{wid}/supersets/group",
            json={"exercise_ids": [str(ex_a), str(ex_b)]},
            headers=headers,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["logs_updated"] == 4
        group_id = body["group_id"]
        assert group_id is not None

        # Все 4 лога теперь имеют этот group_id.
        db_session.expire_all()
        all_logs = (
            await db_session.execute(
                select(ExerciseLog).where(ExerciseLog.workout_id == uuid.UUID(wid))
            )
        ).scalars().all()
        assert {str(log.superset_group_id) for log in all_logs} == {group_id}

        # Разгруппировка.
        r = await client.post(
            f"/api/v1/workouts/{wid}/supersets/ungroup",
            json={"group_id": group_id},
            headers=headers,
        )
        assert r.status_code == 200, r.text
        assert r.json()["logs_updated"] == 4

        db_session.expire_all()
        all_logs = (
            await db_session.execute(
                select(ExerciseLog).where(ExerciseLog.workout_id == uuid.UUID(wid))
            )
        ).scalars().all()
        assert all(log.superset_group_id is None for log in all_logs)


class TestSupersetInheritsOnNewLog:
    async def test_new_log_inherits_group_from_existing(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """REQ-05: добавляем подход в упражнение, которое уже в группе —
        новый лог автоматически попадает в ту же группу."""
        _, headers, ex_a, ex_b = await _seed_user_with_two_exercises(
            db_session, email="ss-2@example.com"
        )
        w = (await client.post(
            "/api/v1/workouts", json={"origin": "freestyle"}, headers=headers
        )).json()
        wid = w["id"]
        # По одному подходу на каждое упражнение, затем группируем.
        for ex_id in (ex_a, ex_b):
            await client.post(
                f"/api/v1/workouts/{wid}/logs",
                json={
                    "exercise_id": str(ex_id),
                    "set_number": 1,
                    "reps": 8,
                    "weight_kg": 60,
                },
                headers=headers,
            )
        grp = await client.post(
            f"/api/v1/workouts/{wid}/supersets/group",
            json={"exercise_ids": [str(ex_a), str(ex_b)]},
            headers=headers,
        )
        group_id = grp.json()["group_id"]

        # Добавляем подход 2 для ex_a — он должен унаследовать group_id.
        r = await client.post(
            f"/api/v1/workouts/{wid}/logs",
            json={
                "exercise_id": str(ex_a),
                "set_number": 2,
                "reps": 8,
                "weight_kg": 65,
            },
            headers=headers,
        )
        assert r.status_code == 201, r.text
        assert r.json()["superset_group_id"] == group_id
