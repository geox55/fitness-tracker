"""Integration: GET /analytics/exercise-progress — spec 010 REQ-09.

Проверяем агрегаты по неделям, изоляцию по пользователю/упражнению,
исключение skipped/незавершённых тренировок, обработку 404 и пустой
истории.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User
from app.domains.catalog.models import Exercise
from app.domains.workouts.models import ExerciseLog, Workout
from app.security import create_token


async def _make_user(session: AsyncSession, *, email: str) -> User:
    user = User(email=email, password_hash="x", email_status="active")
    session.add(user)
    await session.flush()
    return user


async def _make_exercise(
    session: AsyncSession,
    *,
    exercise_id: str,
    name: str,
    name_ru: str | None = None,
) -> Exercise:
    ex = Exercise(
        exercise_id=exercise_id,
        exercise_name=name,
        exercise_name_ru=name_ru,
        primary_muscle_group="chest",
        secondary_muscle_group=None,
        instructions="test",
        equipment="barbell",
        body_region="upper",
    )
    session.add(ex)
    await session.flush()
    return ex


async def _workout(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    performed_at: datetime,
    status: str = "completed",
) -> Workout:
    w = Workout(
        user_id=user_id,
        performed_at=performed_at,
        finished_at=performed_at,
        status=status,
        origin="freestyle",
    )
    session.add(w)
    await session.flush()
    return w


def _log(
    *,
    workout_id: uuid.UUID,
    exercise_id: uuid.UUID,
    set_number: int,
    reps: int,
    weight_kg: float,
    skipped: bool = False,
) -> ExerciseLog:
    return ExerciseLog(
        workout_id=workout_id,
        exercise_id=exercise_id,
        set_number=set_number,
        reps=reps,
        weight_kg=Decimal(str(weight_kg)),
        skipped=skipped,
    )


def _auth(user_id: uuid.UUID) -> dict[str, str]:
    token, _ = create_token(user_id=user_id, kind="access")
    return {"Authorization": f"Bearer {token}"}


class TestExerciseProgress:
    async def test_returns_weeks_with_best_weight_and_e1rm(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Сценарий «нормальный»: две недели логов с PR на второй.
        user = await _make_user(db_session, email="ep1@example.com")
        ex = await _make_exercise(
            db_session,
            exercise_id="bench-press",
            name="Bench Press",
            name_ru="Жим лёжа",
        )

        # Неделя 1 (2026-04-06 пн): 100×5 и 95×8 → e1RM max = 95*(1+8/30)=120.33
        w1 = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        )
        db_session.add(
            _log(workout_id=w1.id, exercise_id=ex.id, set_number=1,
                 reps=5, weight_kg=100.0)
        )
        db_session.add(
            _log(workout_id=w1.id, exercise_id=ex.id, set_number=2,
                 reps=8, weight_kg=95.0)
        )
        # Неделя 2 (2026-04-13 пн): 105×3 → e1RM ≈ 115.5
        w2 = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 13, 10, 0, tzinfo=UTC),
        )
        db_session.add(
            _log(workout_id=w2.id, exercise_id=ex.id, set_number=1,
                 reps=3, weight_kg=105.0)
        )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={ex.id}",
            headers=_auth(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["exercise_id"] == str(ex.id)
        assert body["exercise_title"] == "Жим лёжа"  # name_ru предпочтён
        weeks = body["weeks"]
        assert len(weeks) == 2

        first, second = weeks
        assert first["week_start"] == "2026-04-06"
        assert first["best_weight_kg"] == 100.0
        # 95 * (1 + 8/30) = 120.333... → округлено до 2 знаков
        assert first["best_e1rm_kg"] == 120.33
        assert first["sets"] == 2
        # 5*100 + 8*95 = 500 + 760 = 1260
        assert first["tonnage_kg"] == 1260.0

        assert second["week_start"] == "2026-04-13"
        assert second["best_weight_kg"] == 105.0
        # 105 * (1 + 3/30) = 115.5
        assert second["best_e1rm_kg"] == 115.5
        assert second["sets"] == 1
        assert second["tonnage_kg"] == 3 * 105.0

    async def test_skipped_logs_excluded(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ep-skip@example.com")
        ex = await _make_exercise(
            db_session, exercise_id="squat", name="Squat"
        )
        w = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        )
        db_session.add(
            _log(workout_id=w.id, exercise_id=ex.id, set_number=1,
                 reps=5, weight_kg=100.0, skipped=False)
        )
        # Skipped с PR — не должен попасть в best_weight.
        db_session.add(
            _log(workout_id=w.id, exercise_id=ex.id, set_number=2,
                 reps=1, weight_kg=200.0, skipped=True)
        )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={ex.id}",
            headers=_auth(user.id),
        )
        weeks = resp.json()["weeks"]
        assert weeks[0]["best_weight_kg"] == 100.0
        assert weeks[0]["sets"] == 1

    async def test_in_progress_workouts_excluded(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Логи незавершённой тренировки не идут в прогресс: «состоявшимися»
        # считаются только completed/auto_finished.
        user = await _make_user(db_session, email="ep-inp@example.com")
        ex = await _make_exercise(
            db_session, exercise_id="dl", name="Deadlift"
        )
        w_running = await _workout(
            db_session,
            user_id=user.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
            status="in_progress",
        )
        db_session.add(
            _log(workout_id=w_running.id, exercise_id=ex.id, set_number=1,
                 reps=5, weight_kg=200.0)
        )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={ex.id}",
            headers=_auth(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["weeks"] == []

    async def test_empty_history_returns_empty_weeks(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # У пользователя 0 логов по этому упражнению — это законно, не 404.
        user = await _make_user(db_session, email="ep-empty@example.com")
        ex = await _make_exercise(
            db_session, exercise_id="press", name="OHP", name_ru="Жим стоя"
        )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={ex.id}",
            headers=_auth(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["exercise_title"] == "Жим стоя"
        assert body["weeks"] == []

    async def test_unknown_exercise_returns_404(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ep-404@example.com")
        await db_session.commit()
        bogus = uuid.uuid4()
        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={bogus}",
            headers=_auth(user.id),
        )
        assert resp.status_code == 404
        assert resp.json()["detail"]["error"] == "exercise_not_found"

    async def test_other_users_logs_not_visible(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        alice = await _make_user(db_session, email="ep-alice@example.com")
        bob = await _make_user(db_session, email="ep-bob@example.com")
        ex = await _make_exercise(
            db_session, exercise_id="row", name="Bent Row"
        )
        w = await _workout(
            db_session, user_id=bob.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        )
        db_session.add(
            _log(workout_id=w.id, exercise_id=ex.id, set_number=1,
                 reps=10, weight_kg=80.0)
        )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={ex.id}",
            headers=_auth(alice.id),
        )
        assert resp.status_code == 200
        assert resp.json()["weeks"] == []

    async def test_other_exercises_not_mixed(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Прогресс по жиму не должен включать логи приседа того же юзера.
        user = await _make_user(db_session, email="ep-mix@example.com")
        bench = await _make_exercise(
            db_session, exercise_id="bench-mix", name="Bench"
        )
        squat = await _make_exercise(
            db_session, exercise_id="squat-mix", name="Squat"
        )
        w = await _workout(
            db_session, user_id=user.id,
            performed_at=datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        )
        db_session.add(
            _log(workout_id=w.id, exercise_id=bench.id, set_number=1,
                 reps=5, weight_kg=100.0)
        )
        db_session.add(
            _log(workout_id=w.id, exercise_id=squat.id, set_number=2,
                 reps=5, weight_kg=150.0)
        )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={bench.id}",
            headers=_auth(user.id),
        )
        weeks = resp.json()["weeks"]
        assert weeks[0]["best_weight_kg"] == 100.0  # без приседа

    async def test_from_to_filters_inclusive(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ep-range@example.com")
        ex = await _make_exercise(
            db_session, exercise_id="bench-range", name="Bench"
        )
        for d in (
            datetime(2026, 1, 6, 10, 0, tzinfo=UTC),
            datetime(2026, 2, 16, 10, 0, tzinfo=UTC),
            datetime(2026, 4, 6, 10, 0, tzinfo=UTC),
        ):
            w = await _workout(db_session, user_id=user.id, performed_at=d)
            db_session.add(
                _log(workout_id=w.id, exercise_id=ex.id, set_number=1,
                     reps=5, weight_kg=100.0)
            )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={ex.id}"
            "&from=2026-02-01&to=2026-03-31",
            headers=_auth(user.id),
        )
        weeks = resp.json()["weeks"]
        starts = [w["week_start"] for w in weeks]
        # Только февральская тренировка попадает в диапазон.
        assert starts == ["2026-02-16"]

    async def test_inverted_range_400(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="ep-bad@example.com")
        ex = await _make_exercise(
            db_session, exercise_id="bench-bad", name="Bench"
        )
        await db_session.commit()

        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={ex.id}"
            "&from=2026-03-01&to=2026-02-01",
            headers=_auth(user.id),
        )
        assert resp.status_code == 400
        assert resp.json()["detail"]["error"] == "invalid_range"

    async def test_requires_auth(self, client: AsyncClient) -> None:
        bogus = uuid.uuid4()
        resp = await client.get(
            f"/api/v1/analytics/exercise-progress?exercise_id={bogus}"
        )
        assert resp.status_code == 401
